import copy

import reinforcement


class TicTacToeReverseEnvironment(reinforcement.Environment):
    def __init__(self):
        super().__init__()

        self.state = TicTacToeReverseState(3 ** 9)  # 1回パスした状態から開始することで初手パスを防ぐ

    def valid_actions(self):
        # self.stateから可能な全てのactionを返す
        return self.state.valid_actions()

    def step(self, action):
        # ゲームを1手進める
        self.state = self.state.change(action, 1)

        # 報酬設定
        judge = self.state.judge()
        reward = 1 if judge == 1 else -1 if judge == 2 else 0

        return reward, self.state

    def reset(self):
        self.state = TicTacToeReverseState(3 ** 9)


class TicTacToeReverseState:
    SYMBOL = ('_', 'x', 'o')

    def __init__(self, code=None):
        # 0: blank
        # 1: x
        # 2: o

        self._state = [0] * 9
        self._pass_state = False
        if code is not None:
            # 整数から状態を復元する
            self._pass_state = code // (3 ** 9)  # 0 or 1
            code = code % 3 ** 9

            i = 0
            while code > 0:
                self._state[i] = code % 3
                code = code // 3
                i += 1

        self._judge = None

    def change(self, pos, state):
        # 状態を更新する
        # pos = (x, y)
        # x, y = 0, 1, 2
        if pos == 9:
            clone = self.clone()
            clone._pass_state = True
            return clone
        else:
            if isinstance(pos, tuple):
                x, y = pos
                pos = 3*y+x
            clone = self.clone()
            clone._state[pos] = state

            # 周囲を反転
            clone._reverse(pos - 3)
            clone._reverse(pos + 3)
            if pos % 3 != 0:
                clone._reverse(pos - 3 - 1)
                clone._reverse(pos - 1)
                clone._reverse(pos + 3 - 1)
            if pos % 3 != 2:
                clone._reverse(pos - 3 + 1)
                clone._reverse(pos + 1)
                clone._reverse(pos + 3 + 1)

            clone._pass_state = False

            return clone

    def _reverse(self, pos):
        if 0 <= pos < 9:
            pos_state = self._state[pos]
            if pos_state != 0:
                self._state[pos] = 3 - pos_state

    def code(self):
        # 状態と一対一に対応する整数を返す
        a = 1 if self._pass_state else 0
        for i in reversed(list(range(9))):
            a *= 3
            a += self._state[i]
        return a

    def judge(self):
        # ゲームの状態を判定する
        # 0: in progress
        # 1: x won
        # 2: o won
        # 3: draw
        # -1: impossible state

        if self._judge is None:
            result = [0, 0]

            self._judge_line(result, self._state[0], self._state[1], self._state[2])
            self._judge_line(result, self._state[3], self._state[4], self._state[5])
            self._judge_line(result, self._state[6], self._state[7], self._state[8])
            self._judge_line(result, self._state[0], self._state[3], self._state[6])
            self._judge_line(result, self._state[1], self._state[4], self._state[7])
            self._judge_line(result, self._state[2], self._state[5], self._state[8])
            self._judge_line(result, self._state[0], self._state[4], self._state[8])
            self._judge_line(result, self._state[2], self._state[4], self._state[6])

            if result[0] != 0 and result[1] != 0:
                self._judge = 3
            elif result[0] != 0:
                self._judge = 1
            elif result[1] != 0:
                self._judge = 2
            elif self.list_blank():  # True if not empty
                self._judge = 0
            else:
                self._judge = 3

        return self._judge

    @staticmethod
    def _judge_line(result, pos1, pos2, pos3):
        if pos1 != 0 and pos1 == pos2 == pos3:
            result[pos1 - 1] += 1

    def validate_gameset(self):
        # ゲーム終了を判定する
        if self._judge is None:
            self.judge()
        return self._judge != 0

    def list_blank(self):
        # 空白のマス(=選ぶことのできるマス)を返す
        return [key for key, value in enumerate(self._state) if value == 0]

    def valid_actions(self):
        # 可能な全てのactionを返す
        if self.validate_gameset():
            return []
        else:
            valid_actions = self.list_blank()
            if not self._pass_state:  # パス可能
                valid_actions.append(9)
            return valid_actions

    def reverse(self):
        # 状態を反転させる(x <=> o)
        clone = self.clone()
        for i in range(9):
            a = clone._state[i]
            if a != 0:
                clone._state[i] = 3 - a  # 1 <=> 2

        return clone

    def clone(self):
        s = self.__class__()
        s._state = copy.deepcopy(self._state)
        s._pass_state = self._pass_state
        return s

    @classmethod
    def afterstates(cls):
        # 状態, 行動の対とafterstateの対応を返す
        afterstates = []

        for code in range(2 * 3**9):
            sub = {}
            s = cls(code)

            # 可能な全ての行動を取ってafterstateを保存する
            for a in s.valid_actions():
                after = s.change(a, 1)
                sub[a] = after.code()

            afterstates.append(sub)

        return afterstates

    def __str__(self):
        s = ''
        for i in range(9):
            s += TicTacToeReverseState.SYMBOL[self._state[i]]
            if i % 3 != 2:
                s += ' '
            elif i is not 8:
                s += '\n'
            elif self._pass_state:
                s += ' passed'

        return s


class TicTacToeReverseSelfPlay:
    def __init__(self, agent, save_path_format):
        self.agent = agent
        self.save_path_format = save_path_format

        self.env = TicTacToeReverseEnvironment()
        self.count = 0

        if self.save_path_format is not None:
            self.agent.save(self.save_path_format.format(self.count))

    def __call__(self):
        self.env.reset()

        # sar_o = None
        sar = None  # state, action, reward

        while True:
            sar_o = sar

            state = self.env.get_state()
            action = self.agent.select_action(state.code(), self.env.valid_actions())
            reward, afterstate = self.env.step(action)  # afterstateはstate_oのnext_state

            sar = (state, action, reward)

            if sar_o is not None:
                # 1手前の相手の手に対する報酬が得られたので、ここで学習する
                state_o, action_o, _ = sar_o
                self.agent.update(state_o.code(), action_o, -reward, afterstate.reverse().code(), self.env.valid_actions())

            if afterstate.validate_gameset():
                # ゲームが終了した場合、最後の状態も評価する
                self.agent.update(state.code(), action, reward, afterstate.code(), self.env.valid_actions())

                self.count += 1

                # 10000ゲームに1回結果を表示
                if self.count % 10000 == 0:
                    judge = afterstate.judge()
                    print('game {}: {}'.format(self.count, 'win' if judge == 1 else 'lose' if judge == 2 else 'draw'))
                    print(afterstate)

                    # # エージェントを保存
                    if self.save_path_format is not None:
                        self.agent.save(self.save_path_format.format(self.count))

                return

            # 反転して手番を交代する
            afterstate = afterstate.reverse()
            self.env.set_state(afterstate)


if __name__ == '__main__':
    n_game = 1000000  # 学習ゲーム数

    import datetime
    now = datetime.datetime.now()
    save_path_format = 'save/' + now.strftime('%Y%m%d_%H%M%S') + '_tic_tac_toe_reverse_q_{}'

    # エージェントと学習クラスの初期化
    agent = reinforcement.QAfterStateAgent(TicTacToeReverseState.afterstates(), epsilon=0.5, explore=True)
    selfplay = TicTacToeReverseSelfPlay(agent, save_path_format)

    for _ in range(n_game):
        selfplay()

    print('total time: {}'.format(datetime.datetime.now() - now))
