from tic_tac_toe import *


class Game:
    def __init__(self, env, agent):
        self.env = env
        self.agent = agent

    def __call__(self):
        # ゲーム実行
        # 0: 進行中
        # 1: プレイヤーの勝ち
        # 2: プレイヤーの負け
        # 3: 引き分け
        # 4: 降参
        self.env.reset()

        print()
        first = self.select_first()
        players_turn = first

        while True:
            if players_turn:
                result = self.player_play(first)
                if result is not 0:
                    return result
                players_turn = not players_turn

            if not players_turn:
                result = self.computer_play(first)
                if result is not 0:
                    return result
                players_turn = not players_turn

    @staticmethod
    def select_first():
        # 先後を選択させる
        a = None
        while a is None:
            a = input('先後を選んでください。(0:先, 1:後)\n')
            try:
                a = int(a)
                assert a == 0 or a == 1
            except Exception:
                a = None

        if a == 0:
            print('あなたは先手(x)です。')
            return True
        else:
            print('あなたは後手(o)です。')
            return False

    def select_position(self):
        # プレイヤーに手を選択させる
        a = None
        while a is None:
            a = input('打つ場所を指定してください。(r: 降参, h: ヒント)\n')
            if a == 'h':
                # ヒントを表示
                print('ヒント')
                self.hint()
                a = None
            elif a == 'r':
                # 降参してゲーム終了
                print('降参しました。')
                return None
            else:
                # (横, 縦)のtupleとして解釈
                try:
                    a = a.split(' ')
                    a = (int(a[0]), int(a[1]))
                    assert 0 <= a[0]
                    assert a[0] <= 2
                    assert 0 <= a[1]
                    assert a[1] <= 2
                    a = a[1]*3 + a[0]
                    assert a in self.env.valid_actions()
                except Exception:
                    a = None

        return a

    def player_play(self, first):
        # プレイヤーに手を選ばせる
        action = self.select_position()
        if action is None:
            return 4
        _, afterstate = self.env.step(action)

        return self.judge(not first, first)

    def computer_play(self, first):
        # コンピューターが手を選ぶ
        print('コンピューターが手を選びます。')
        state = self.env.get_state()
        action = self.agent.select_action(state.code(), self.env.valid_actions())
        _, afterstate = self.env.step(action)

        return self.judge(first, first)

    def judge(self, reverse, first):
        # 勝敗を判定して手番を相手に渡す
        # reverse: 盤面が本来の状態から反転しているか
        # first: プレイヤーが先手か
        state = self.env.get_state()
        if reverse:
            # 判定前に盤面を本来の状態に戻す
            state = state.reverse()
            self.env.set_state(state)

        # 本来の状態を表示する
        print(state)

        if state.validate_gameset():
            if state.judge() == 3:
                print('引き分けです。')
                return 3
            elif (state.judge() != 1) ^ first:
                # (先手が勝ち and 先手がプレイヤー) or
                # (先手が負け and 先手がコンピューター)
                print('あなたの勝ちです。')
                return 1
            else:
                # (先手が負け and 先手がプレイヤー) or
                # (先手が勝ち and 先手がコンピューター)
                print('あなたの負けです。')
                return 2

        if not reverse:
            # 判定後に盤面を反転させて手番を渡す
            state = state.reverse()
            self.env.set_state(state)

        return 0

    def hint(self):
        # ヒント表示
        # Qを100倍して表示する
        q_s = agent.q_s(self.env.state.code())
        valid_q_s = {}
        for valid_action in self.env.valid_actions():
            valid_q_s[(valid_action % 3, valid_action // 3)] = q_s[valid_action] * 100

        format = '{} {}: {:>6.2f}'

        argmax = max(valid_q_s, key=valid_q_s.get)

        for key, value in valid_q_s.items():
            s = format.format(key[0], key[1], value)
            if key == argmax:
                print(self.red_format(s))
            else:
                print(s)

    @staticmethod
    def red_format(s):
        # コンソール出力を赤くする
        return '\033[31m{}\033[0m'.format(s)


if __name__ == '__main__':
    # 環境とエージェントの初期化
    # explore=Trueならたまに間違える
    env = TicTacToeEnvironment()
    agent = reinforcement.QAfterStateAgent(TicTacToeState.afterstates(), explore=False)

    # Q tableを読み込む
    agent.load('save/tic_tac_toe_q')

    game = Game(env, agent)

    result = [0, 0, 0, 0]
    while True:
        result[game() - 1] += 1  # ゲームを実行して結果を保存
        print('勝ち:{}, 負け:{}, 引き分け:{}, 降参:{}'.format(*result))
