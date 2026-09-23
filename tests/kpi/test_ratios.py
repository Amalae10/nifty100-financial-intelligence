from src.analytics.ratios import (
    net_profit_margin,
    operating_profit_margin,
    check_opm,
    roe,
    roce,
    roa,
    roce_benchmark,
    debt_to_equity,
    interest_coverage,
    icr_label,
    high_leverage,
    asset_turnover

)


def test_net_profit_margin():
    assert net_profit_margin(200, 1000) == 20


def test_zero_sales():
    assert net_profit_margin(100, 0) is None


def test_operating_margin():
    assert operating_profit_margin(300, 1000) == 30


def test_opm_mismatch():
    assert check_opm(30, 25) is True


def test_roe():
    assert roe(200, 500, 500) == 20


def test_negative_equity():
    assert roe(100, 100, -200) is None


def test_roce():
    assert roce(200, 400, 400, 200) == 20


def test_roa_zero_assets():
    assert roa(100, 0) is None

def test_financial_roce():
    assert roce_benchmark("Financials") == "SECTOR"

def test_debt_free_de():
    assert debt_to_equity(0,500,500) == 0

def test_de_ratio():
    assert debt_to_equity(500, 500, 500) == 0.5

def test_icr_zero():
    assert interest_coverage(100,20,0) is None

def test_icr():
    assert interest_coverage(100,20,40) == 3

def test_icr_label():
    assert icr_label(None)== "Debt Free"

def test_high_leverage():
    assert high_leverage(6,"Industrials") is True

def test_financial_leverage():
    assert high_leverage(6,"Financials") is False

def test_asset_turnover_zero():
    assert asset_turnover(100,0) is None

def test_roa_normal():
    from src.analytics.ratios import roa
    assert roa(100, 1000) == 10


def test_net_debt():
    from src.analytics.ratios import net_debt
    assert net_debt(500, 200) == 300


def test_icr_warning():
    from src.analytics.ratios import icr_warning
    assert icr_warning(1.0) is True
    assert icr_warning(2.0) is False