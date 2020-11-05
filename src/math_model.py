import numpy as np
from logger import log_settings
from typing import Dict

app_log = log_settings()


class MathModel:
    days_params = {"0": {"params": {"p0": 68.6781539999999,
                                    "p1": - 0.87130515892857,
                                    "p2": 0.00205254330357142}},
                   "1": {"params": {"p0": 82.9741629999999,
                                    "p1": -0.745074860714284,
                                    "p2": 0.0015394169642857}},
                   "2": {"params": {"p0": 93.4626439999999,
                                    "p1": -0.630388267857141,
                                    "p2": 0.00134698660714284}},
                   "3": {"params": {"p0": 97.70111,
                                    "p1": -0.414869517857144,
                                    "p2": 4.48986607142863E-4}},
                   "4": {"params": {"p0": 100.79021,
                                    "p1": -0.297618125,
                                    "p2": 3.84843750000002E-4}},
                   "5": {"params": {"p0": 101.364984,
                                    "p1": -0.188835857142858,
                                    "p2": 2.56582142857146E-4}},
                   "6": {"params": {"p0": 101.436805,
                                    "p1": -0.111094839285714,
                                    "p2": 1.92433035714285E-4}},
                   "7": {"params": {"p0": 99.856335,
                                    "p1": 0.00307787500000054,
                                    "p2": -3.84843750000007E-4}}
                   }

    def __init__(self, str_ind: float, cs=70.0, cs_high=80.0, cs_low=60.0):
        self.stringency_index = str_ind
        self.contact_strategy = cs
        self.contact_strategy_high = cs_high
        self.contact_strategy = cs_low
        self.repr_number = 1

    @staticmethod
    def risk_index(repr_number: float) -> float:
        return repr_number * 250 - 200

    @property
    def testing_delay(self) -> float:
        return 7 - 0.07 * self.stringency_index

    @property
    def fit_day_params(self) -> Dict:
        day1 = str(int(self.testing_delay))
        day2 = str(int(self.testing_delay)+1)
        test_delay_dict = {"begin": self.days_params.get(day1, None),
                           "end": self.days_params.get(day2, None)}
        return test_delay_dict

    @staticmethod
    def fit_slope(begin_p: float, end_p: float) -> float:
        return end_p - begin_p

    @staticmethod
    def fit_intercept(begin_p: float, end_p) -> float:
        return begin_p

    def fit_parameter(self, begin_p: float, end_p: float) -> float:
        fit_dict = self.fit_day_params
        if fit_dict and fit_dict.get("begin", None) is not None and fit_dict.get("end", None) is not None:
            slope = self.fit_slope(fit_dict.get())
        else:
            app_log.error("Main dictionary does not exists or not full")


if __name__ == "__main__":
    a = MathModel(70).get_testing_delay
    print(a, int(a))
    b = MathModel(70).get_fit_day_params
    print(b)