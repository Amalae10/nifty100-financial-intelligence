from src.analytics.cagr import cagr

def test_normal():
    value, flag = cagr(100, 200, 5)
    assert value is not None
    assert flag == "OK"

def test_zero_base():
    assert cagr(0, 100, 5)[1] == "ZERO_BASE"

def test_turnaround():
    assert cagr(-100, 200, 5)[1] == "TURNAROUND"

def test_decline():
    assert cagr(100, -50, 5)[1] == "DECLINE_TO_LOSS"

def test_both_negative():
    assert cagr(-100, -50, 5)[1] == "BOTH_NEGATIVE"

def test_insufficient():
    assert cagr(100, 200, 0)[1] == "INSUFFICIENT"

def test_three_year():
    assert cagr(100, 133.1, 3)[0] is not None

def test_five_year():
    assert cagr(100, 161.05, 5)[0] is not None

def test_ten_year():
    assert cagr(100, 259.37, 10)[0] is not None

def test_flag_ok():
    assert cagr(100, 120, 3)[1] == "OK"