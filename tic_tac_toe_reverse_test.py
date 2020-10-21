

if __name__ == '__main__':
    from tic_tac_toe_test import *

    import matplotlib.pyplot as plt
    import numpy as np

    from reinforcement import QAfterStateAgent
    from tic_tac_toe_reverse import *

    env = TicTacToeReverseEnvironment()
    afterstates = TicTacToeReverseState.afterstates()

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

    save_path_format = 'save/20201020_142341_tic_tac_toe_reverse_q_{}'
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

