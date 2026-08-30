from src.analytics.cashflow_kpis import *


def test_fcf():
    assert fcf(500, -200) == 300


def test_pat_zero():
    assert cfo_pat_ratio(500, 0) is None


def test_high_quality():
    assert cfo_quality([1.2, 1.1, 1.3]) == "High Quality"


def test_moderate():
    assert cfo_quality([0.6, 0.8, 0.7]) == "Moderate"


def test_accrual_risk():
    assert cfo_quality([0.2, 0.3, 0.4]) == "Accrual Risk"


def test_capex():
    assert capex_intensity(-100, 1000) == "Capital Intensive"


def test_fcf_conversion():
    assert fcf_conversion(200, 400) == 50


def test_reinvestor():
    assert allocation(500, -200, -100, 0.8)[1] == "Reinvestor"


def test_shareholder_returns():
    assert allocation(500, -200, -100, 1.2)[1] == "Shareholder Returns"


def test_distress():
    assert allocation(-100, 50, 100)[1] == "Distress Signal"