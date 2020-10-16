from abc import ABCMeta, abstractmethod
import random
import pickle


class Environment(metaclass=ABCMeta):
    def __init__(self):
        self.state = None

    def get_state(self):
        return self.state

    def set_state(self, state):
        self.state = state

    @abstractmethod
    def valid_actions(self):
        pass

    @abstractmethod
    def step(self, action):
        pass


class Agent(metaclass=ABCMeta):
    @abstractmethod
    def policy(self, action, state):
        pass

    @abstractmethod
    def select_action(self, state, valid_actions):
        pass

    @abstractmethod
    def update(self, *data):
        pass

    @staticmethod
    def _save(path, data):
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def _load(path):
        with open(path, 'rb') as f:
            return pickle.load(f)


# class QAgent(Agent):
#     def __init__(self, states=1):
#         self.alpha = 0.01
#         self.gamma = 0.99
#         self.epsilon = 0.1
#
#         self.q = [{}]*states
#
#     def policy(self, state, action):
#         policy_s = self.policy_s(state)
#         if action not in policy_s:
#             return policy_s[action]
#         else:
#             policy_s[action] = 0
#             return 0
#
#     def policy_s(self, state):
#         return self.q[state]
#
#     def select_action(self, state, valid_actions, explore=False):
#         # eps_greedy
#         if explore and random.random() < self.epsilon:
#             return random.choice(valid_actions)
#         else:
#             return max(self.policy_s(state))
#
#     def update(self, state, action, reward, next_state):
#         q = self.q[state][action]
#         max_q = max(self.policy_s(next_state).values())
#
#         self.q[state][action] += self.alpha*(reward + self.gamma*max_q - q)


class QAfterStateAgent(Agent):
    def __init__(self, after_states, alpha=0.1, epsilon=0.1, gamma=0.9, explore=False):
        self.alpha = alpha
        self.epsilon = epsilon
        self.gamma = gamma

        self.q_afterstates = [0]*len(after_states)  # initial value
        self.afterstates = after_states

        self.explore = explore

    def q(self, state, action):
        # Q(s, a)
        return self.q_afterstates[self.afterstates[state][action]]

    def q_s(self, state):
        # Q(s)
        policy_s = {}
        for key, value in self.afterstates[state].items():
            policy_s[key] = self.q_afterstates[value]
        return policy_s

    def policy(self, state, action):
        # pi(s, a)
        q_s = self.q_s(state)
        key = max(q_s, key=q_s.get)

        return 1 if action == key else 0

    def select_action(self, state, valid_actions):
        # epsilon-greedy
        if self.explore and random.random() < self.epsilon:
            return random.choice(valid_actions)
        else:
            q_s = self.q_s(state)
            valid_q = {action: q_s[action] for action in valid_actions}
            return max(valid_q, key=valid_q.get)

    def update(self, *data):
        # Q-learning
        # Q(after(s, a)) <- Q(after(s, a)) + a*(r + g*max{Q(after(next_s, next_a)); next_a} - Q(after(s, a))))
        state, action, reward, next_state, valid_next_actions = data

        afterstate = self.afterstates[state][action]
        q = self.q_afterstates[afterstate]

        valid_next_q = [self.q_s(next_state)[next_action] for next_action in valid_next_actions]
        max_q = max(valid_next_q) if valid_next_q else 0

        self.q_afterstates[afterstate] += self.alpha * (reward + self.gamma*max_q - q)

    def save(self, path):
        self._save(path, self.q_afterstates)

    def load(self, path):
        self.q_afterstates = self._load(path)
