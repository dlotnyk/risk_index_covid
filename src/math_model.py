from logger import log_settings
from typing import Dict
from pprint import pprint

app_log = log_settings()


class MathModel:
    s_dict_begin = "begin"
    s_dict_end = "end"
    s_dict_result = "result"
    s_param_0 = "p0"
    s_param_1 = "p1"
    s_param_2 = "p2"
    days_params = {"0": {s_param_0: 68.6781539999999,
                         s_param_1: - 0.87130515892857,
                         s_param_2: 0.00205254330357142},
                   "1": {s_param_0: 82.9741629999999,
                         s_param_1: -0.745074860714284,
                         s_param_2: 0.0015394169642857},
                   "2": {s_param_0: 93.4626439999999,
                         s_param_1: -0.630388267857141,
                         s_param_2: 0.00134698660714284},
                   "3": {s_param_0: 97.70111,
                         s_param_1: -0.414869517857144,
                         s_param_2: 4.48986607142863E-4},
                   "4": {s_param_0: 100.79021,
                         s_param_1: -0.297618125,
                         s_param_2: 3.84843750000002E-4},
                   "5": {s_param_0: 101.364984,
                         s_param_1: -0.188835857142858,
                         s_param_2: 2.56582142857146E-4},
                   "6": {s_param_0: 101.436805,
                         s_param_1: -0.111094839285714,
                         s_param_2: 1.92433035714285E-4},
                   "7": {s_param_0: 99.856335,
                         s_param_1: 0.00307787500000054,
                         s_param_2: -3.84843750000007E-4}
                   }

    def __init__(self, stringency_index: float,
                 contact_strategy=70.0,
                 contact_strategy_high=80.0,
                 contact_strategy_low=60.0):
        """
        Init metod for Math calculations
        :param stringency_index: main parameter stringency index
        :param contact_strategy: default is 70
        :param contact_strategy_high: high error bar for estimation
        :param contact_strategy_low: low error bar for estimation
        """
        self.stringency_index = stringency_index
        self.contact_strategy = contact_strategy
        self.contact_strategy_high = contact_strategy_high
        self.contact_strategy_low = contact_strategy_low
        self._fit_dict: Dict = dict()
        self.init_fit_dict()

    @property
    def fit_dict(self):
        """
        Returns fit dictionary contains fitting parameters of testing delay at previuos day or `begin`,
        next day or `end` and the resulting `result`
        :return:
        """
        return self._fit_dict

    def init_fit_dict(self):
        """
        Initiates fit dictionary based on testing delay and days_param dictionary
        :return: fit_dict
        """
        day1 = str(int(self.testing_delay))
        day2 = str(int(self.testing_delay)+1)
        self._fit_dict = {self.s_dict_begin: self.days_params.get(day1, None),
                          self.s_dict_end: self.days_params.get(day2, None),
                          self.s_dict_result: {}}

    @property
    def testing_delay(self) -> float:
        """
        Returns resting delay based on stringency index as
        TD = 7 - 0.07 * SI
        Should be 0 < TD < 7
        :return: testing_delay
        """
        return 7 - 0.07 * self.stringency_index

    @staticmethod
    def fit_slope(begin_p: float, end_p: float) -> float:
        """
        Slope of the parameter fit. Such simple because days difference = 1
        slope = (p_e - p_b)(days_difference)
        :param begin_p: parameter for day before
        :param end_p: paramter for day after
        :return: slope
        """
        return end_p - begin_p

    @staticmethod
    def fit_intercept(begin_p: float) -> float:
        """
        returns intercept for parameter fit
        :param begin_p:
        :return: intercept
        """
        return begin_p

    def fit_parameters(self) -> None:
        """
        Calculates parameters for resulting quadratic fit.
        Updates fit_dict under key `result`
        """
        if self.fit_dict and self.fit_dict.get(self.s_dict_begin, None) is not None \
                and self.fit_dict.get(self.s_dict_end, None) is not None:
            for key1, key2 in zip(list(self.fit_dict.get(self.s_dict_begin).keys()),
                                  list(self.fit_dict.get(self.s_dict_end))):
                slope = self.fit_slope(self.fit_dict["begin"][key1], self.fit_dict["end"][key2])
                intercept = self.fit_intercept(self.fit_dict["begin"][key1])
                x = self.testing_delay - int(self.testing_delay)
                res = slope * x + intercept
                self._fit_dict["result"].update({key1: res})
            app_log.debug("Fit parameters for RI are calculated")
        else:
            app_log.error("Main dictionary does not exists or not full")

    def get_risk_index(self, cont_strat: float) -> float:
        """
        Returns the risk index based on `result` quadratic fit
        :param cont_strat:
        :return: RI
        """
        if self.fit_dict.get(self.s_dict_result):
            x0 = self.fit_dict[self.s_dict_result][self.s_param_0]
            x1 = self.fit_dict[self.s_dict_result][self.s_param_1] * cont_strat
            x2 = self.fit_dict[self.s_dict_result][self.s_param_2] * cont_strat * cont_strat
            return x0 + x1 + x2
        else:
            app_log.error("Data are not fitted yet")

    @property
    def get_main_data(self):
        """
        :return: tuple of RI for Contact Strategies
        """
        return self.get_risk_index(self.contact_strategy), self.get_risk_index(self.contact_strategy_low), self.get_risk_index(self.contact_strategy_high)

    @property
    def main_math(self):
        """
        main part. Executes all parts
        :return: tuple of RI for Contact Strategies user defined or default 60-low, 70-default, 80-high
        """
        self.fit_parameters()
        app_log.info(f"RI are: {self.get_main_data}")
        return self.get_main_data


if __name__ == "__main__":
    app_log.info("math_model starts")
    A = MathModel(22)
    print(f"Testing delay: {A.testing_delay}")
    A.fit_parameters()
    pprint(A.fit_dict)
    print(f"Def rist {A.get_risk_index(A.contact_strategy)}")
    print(A.get_main_data)
    print(MathModel(60).main_math)
    print(MathModel(stringency_index=85,
                    contact_strategy=65,
                    contact_strategy_high=90,
                    contact_strategy_low=55).main_math)
    app_log.info("math_model stops")
