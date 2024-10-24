import numpy as np
from scipy import stats

from .agents import Trader
from .model import SugarscapeG1mt, flatten


def check_slope(y, increasing):
    x = range(len(y))
    slope, intercept, _, p_value, _ = stats.linregress(x, y)
    result = (slope > 0) if increasing else (slope < 0)
    # p_value for significance.
    assert result and p_value < 0.05, (slope, p_value)


def test_decreasing_price_variance():
    # The variance of the average trade price should decrease over time (figure IV-3)
    # See Growing Artificial Societies p. 109.
    model = SugarscapeG1mt(42)
    model.datacollector._new_model_reporter(
        "price_variance",
        lambda m: np.var(
            flatten([a.prices for a in m.agents_by_type[Trader].values()])
        ),
    )
    model.run_model(step_count=50)

    df_model = model.datacollector.get_model_vars_dataframe()

    check_slope(df_model.price_variance, increasing=False)


def test_carrying_capacity():
    def calculate_carrying_capacities(enable_trade):
        carrying_capacities = []
        visions = range(1, 10)
        for vision_max in visions:
            model = SugarscapeG1mt(vision_max=vision_max, enable_trade=enable_trade)
            model.run_model(step_count=50)
            carrying_capacities.append(len(model.agents_by_type[Trader]))
        return carrying_capacities

    # Carrying capacity should increase over mean vision (figure IV-6).
    # See Growing Artificial Societies p. 112.
    carrying_capacities_with_trade = calculate_carrying_capacities(True)
    check_slope(
        carrying_capacities_with_trade,
        increasing=True,
    )
    # Carrying capacity should be higher when trade is enabled (figure IV-6).
    carrying_capacities_no_trade = calculate_carrying_capacities(False)
    check_slope(
        carrying_capacities_no_trade,
        increasing=True,
    )

    t_statistic, p_value = stats.ttest_rel(
        carrying_capacities_with_trade, carrying_capacities_no_trade
    )
    # t_statistic > 0 means carrying_capacities_with_trade has larger values
    # than carrying_capacities_no_trade.
    # p_value for significance.
    assert t_statistic > 0 and p_value < 0.05


# TODO:
# 1. Reproduce figure IV-12 that the log of average price should decrease over average agent age
# 2. Reproduce figure IV-13 that the gini coefficient on trade should decrease over mean vision, and should be higher with trade
# 3. a stricter test would be to ensure the amount of variance of the trade price matches figure IV-3
