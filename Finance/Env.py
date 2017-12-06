import pickle
import numpy as np


class Loader(object):
    def __init__(self, base_dir="../data/"):
        self.base_dir = base_dir
        self.data_info = {
            "000300": {
                "file": "000300.pkl",
                "start": "2007-01-04",
                "end": "2016-12-30",
                "level": "minute",
                "info": "沪深300指数",
                "source": "米筐量化平台"
            }
        }

    def load(self, code):
        if code not in self.data_info:
            print("Invalid code: " + str(code))

        with open(self.base_dir + self.data_info[code]["file"], "rb") as f:
            return pickle.load(f), self.data_info[code]

    def get_data_list(self):
        [print(self.data_info[key]) for key in self.data_info]


class Env(object):
    def __init__(self, series):
        # series:       #   #   ... #   #   #   #   #   #  ...
        # obs/state:   (240*10)    [f] [f] [f] [f] [f] [f] ...
        # pt:                       0   1   2   3   4   5  ...
        # rw:

        self.data = series
        self.obs = []
        self.__DDRLFFSR__()
        self.pt = 0
        self.is_done = False

    def __DDRLFFSR__(self):
        # Use last 45min, 3h, 5h, 1day, 3day, 10day as state
        # 240 point a day
        # t-240*10, t-240*3, t-240, t-300, t-180, t-45:t
        self.obs.clear()
        for i in range(240 * 10, self.data.size):
            r = [self.data[i - 240 * 10], self.data[i - 240 * 3], self.data[i - 240], self.data[i - 300],
                 self.data[i - 180]]
            for j in range(45, 0, -1):
                r.append(self.data[i - j])
            self.obs.append(np.array(r))

    # action: 1 = unchange, 0 = change
    # hold: 1 = hold, -1 = unhold
    def act(self, action, hold):
        # Return new_state, reward, is_done

        # Because both the return of sigmod and np.rand.ranint is 0/1
        # Should be encoded into -1/1
        action = -1 if action == 0 else action
        if self.pt > len(self.obs):
            self.is_done = True
            return self.obs[-1], hold * (self.data[-1] - self.data[-2]), self.is_done

        self.pt += 1

        return self.obs[self.pt], hold * action * (
            self.data[self.pt + 240 * 10] - self.data[self.pt + 240 * 10 - 1]), self.is_done

    def reset(self):
        self.pt = 0
        self.is_done = False
        return self.obs[self.pt]

    def clear(self):
        self.data = None
        self.obs.clear()
        self.pt = 0
