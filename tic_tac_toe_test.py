

def test_game(env, agent1, agent2, n_game=1000):
    log = {
        'first_move_win': 0,
        'first_move_lose': 0,
        'first_move_draw': 0,
        'second_move_win': 0,
        'second_move_lose': 0,
        'second_move_draw': 0,
    }

    for _ in range(n_game):
        result = game(env, agent1, agent2, True)  # 先手
        if result == 1:
            log['first_move_win'] += 1
        elif result == -1:
            log['first_move_lose'] += 1
        elif result == 0:
            log['first_move_draw'] += 1

        result = game(env, agent1, agent2, False)  # 後手
        if result == 1:
            log['second_move_win'] += 1
        elif result == -1:
            log['second_move_lose'] += 1
        elif result == 0:
            log['second_move_draw'] += 1

    return log


def game(env, agent1, agent2, agent1_first):
    env.reset()

    agent1_move = agent1_first

    while True:
        agent = agent1 if agent1_move else agent2

        state = env.get_state()
        action = agent.select_action(state.code(), env.valid_actions())
        _, afterstate = env.step(action)

        if afterstate.validate_gameset():
            judge = afterstate.judge()
            if judge == 1:
                return 1 if agent1_move else -1
            elif judge == 2:  # 通らないはず
                return -1 if agent1_move else 1
            elif judge == 3:
                return 0

        # 反転して手番を交代する
        afterstate = afterstate.reverse()
        env.set_state(afterstate)

        agent1_move = not agent1_move


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    import numpy as np

    from reinforcement import QAfterStateAgent
    from tic_tac_toe import *

    env = TicTacToeEnvironment()
    afterstates = TicTacToeState.afterstates()

    randomAgent = QAfterStateAgent(afterstates, epsilon=1, explore=True)
    agent = None

    plot_data = {
        'random': {
            'first_move_win': [],
            'first_move_lose': [],
            'first_move_draw': [],
            'second_move_win': [],
            'second_move_lose': [],
            'second_move_draw': [],
        },
        'prev': {
            'first_move_win': [],
            'first_move_lose': [],
            'first_move_draw': [],
            'second_move_win': [],
            'second_move_lose': [],
            'second_move_draw': [],
        }
    }

    step = 10000
    n = 1000000
    test_games = 1000

    save_path_format = 'save/20201015_190846_tic_tac_toe_q_{}'
    for i in range(n // step + 1):
        prev_agent = agent
        agent = QAfterStateAgent(afterstates)
        agent.load(save_path_format.format(i * step))

        log = test_game(env, agent, randomAgent, test_games)
        for key in log:
            plot_data['random'][key].append(log[key])

        if prev_agent is not None:
            log = test_game(env, agent, prev_agent, 1)
            for key in log:
                plot_data['prev'][key].append(log[key])

        print('{}/{}'.format(i * step, n))

    fig = plt.figure()
    ax1 = fig.add_subplot(2, 2, 1, title='vs random agent (first move)')
    ax2 = fig.add_subplot(2, 2, 2, title='vs random agent (second move)')
    ax3 = fig.add_subplot(2, 2, 3, title='vs previous agent (first move)')
    ax4 = fig.add_subplot(2, 2, 4, title='vs previous agent (second move)')

    x = np.arange(0, n + 1, step)
    ax1.stackplot(x,
                  np.array(plot_data['random']['first_move_win']),
                  np.array(plot_data['random']['first_move_draw']),
                  np.array(plot_data['random']['first_move_lose']))
    ax2.stackplot(x,
                  np.array(plot_data['random']['second_move_win']),
                  np.array(plot_data['random']['second_move_draw']),
                  np.array(plot_data['random']['second_move_lose']))

    x = np.arange(step, n + 1, step)
    ax3.stackplot(x,
                  np.array(plot_data['prev']['first_move_win']),
                  np.array(plot_data['prev']['first_move_draw']),
                  np.array(plot_data['prev']['first_move_lose']))
    ax4.stackplot(x,
                  np.array(plot_data['prev']['second_move_win']),
                  np.array(plot_data['prev']['second_move_draw']),
                  np.array(plot_data['prev']['second_move_lose']))

    plt.show()

