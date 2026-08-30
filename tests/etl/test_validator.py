import pandas as pd

from src.etl.validator import (check_pk,
                               check_company_year,
                               check_fk,
                               check_bs_balance,
                               check_opm,
                               check_dividend_cap,
                               check_positive_sales,
                               check_year_format,
                               check_ticker_format,
                               check_net_cash,
                               check_fixed_assets,
                               check_tax_range,
                               check_url,
                               check_eps_sign,
                               check_strict_balance,
                               check_coverage
)


def test_pk():
    df = pd.DataFrame({"id": [1, 2, 2]})
    assert check_pk(df, "id") == 1


def test_positive():
    df = pd.DataFrame({"sales": [100, 200, -10]})
    assert check_positive_sales(df) == 1

def test_dq01_no_duplicates():
    df = pd.DataFrame({"id": [1, 2, 3, 4]})
    assert check_pk(df, "id") == 0

def test_dq02_company_year():
    df = pd.DataFrame({
        "company_id": [1, 1, 2, 1],
        "year": [2024, 2024, 2024, 2023]
    })

    assert check_company_year(df) == 1

def test_dq03_fk():
    companies = pd.DataFrame({
        "id": [1, 2, 3]
    })

    data = pd.DataFrame({
        "company_id": [1, 2, 99]
    })

    assert check_fk(data, companies, "company_id") == 1


def test_dq03_valid_fk():
    companies = pd.DataFrame({
        "id": [1, 2, 3]
    })

    data = pd.DataFrame({
        "company_id": [1, 2, 3]
    })

    assert check_fk(data, companies, "company_id") == 0

def test_dq04_bs_balance():
    df = pd.DataFrame({
        "total_assets": [1000, 1000],
        "total_liabilities": [1000, 900]
    })

    assert check_bs_balance(df) == 1



def test_dq05_opm():
    df = pd.DataFrame({
        "sales": [1000],
        "operating_profit": [200],
        "opm_percentage": [20]
    })

    assert check_opm(df) == 0

def test_dq06_positive_sales():
    df = pd.DataFrame({
        "sales": [100, 200, 0, -10]
    })

    assert check_positive_sales(df) == 2

def test_dq07_year_format():
    df = pd.DataFrame({
        "year": ["2024-03", "2023-12", "Mar 2024"]
    })

    assert check_year_format(df) == 1

def test_dq08_ticker_format():
    df = pd.DataFrame({
        "company_id": ["TCS", " reliance ", "A", "THISISWAYTOOLONG"]
    })

    assert check_ticker_format(df) == 2

def test_dq09_net_cash():
    df = pd.DataFrame({
        "operating_activity": [500, 500],
        "investing_activity": [-200, -200],
        "financing_activity": [-100, -100],
        "net_cash_flow": [205, 250]
    })

    assert check_net_cash(df) == 1

def test_dq10_fixed_assets():
    df = pd.DataFrame({
        "fixed_assets": [100, 0, -50]
    })

    assert check_fixed_assets(df) == 1

def test_dq11_tax_range():
    df = pd.DataFrame({
        "tax_percentage": [25, 60, -5, 70]
    })

    assert check_tax_range(df) == 2

def test_dq12_dividend_cap():
    df = pd.DataFrame({
        "dividend_payout": [25, 100, 200, 250]
    })

    assert check_dividend_cap(df) == 1

def test_dq13_url(monkeypatch):
    class Response:
        status_code = 200

    monkeypatch.setattr(
        "src.etl.validator.requests.head",
        lambda url, timeout: Response()
    )

    assert check_url("https://example.com/report.pdf") == False

def test_dq14_eps_sign():
    df = pd.DataFrame({
        "net_profit": [100, 200, -50],
        "eps": [10, -2, -5]
    })

    assert check_eps_sign(df) == 1

def test_dq15_strict_balance():
    df = pd.DataFrame({
        "total_liabilities": [1000, 900],
        "total_assets": [1000, 1000]
    })

    assert check_strict_balance(df) == 1

def test_dq16_coverage():
    df = pd.DataFrame({
        "company_id": ["TCS"] * 5 + ["INFY"] * 3,
        "year": [
            2020, 2021, 2022, 2023, 2024,
            2022, 2023, 2024
        ]
    })

    assert check_coverage(df) == 1