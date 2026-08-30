def net_profit_margin(net_profit, sales):
    if sales == 0:
        return None

    return (net_profit / sales) * 100


def operating_profit_margin(operating_profit, sales):
    if sales == 0:
        return None

    return (operating_profit / sales) * 100


def check_opm(computed_opm, source_opm):
    if computed_opm is None or source_opm is None:
        return False

    return abs(computed_opm - source_opm) > 1


def roe(net_profit, equity_capital, reserves):
    equity = equity_capital + reserves

    if equity <= 0:
        return None

    return (net_profit / equity) * 100


def roce(ebit, equity_capital, reserves, borrowings):
    capital = equity_capital + reserves + borrowings

    if capital <= 0:
        return None

    return (ebit / capital) * 100


def roa(net_profit, total_assets):
    if total_assets == 0:
        return None

    return (net_profit / total_assets) * 100

def roce_benchmark(sector):
    return "SECTOR" if sector =="Financials" else "STANDARD"

def debt_to_equity(debt, equity, reserves):
    total = equity + reserves
    if debt == 0:
        return 0
    return None if total <= 0 else debt / total

def interest_coverage(op_profit, other_income, interest):
    return None if interest == 0 else (op_profit + other_income) / interest

def icr_label(icr):
    return "Debt Free" if icr is None else ""

def icr_warning(icr):
    return icr is not None and icr < 1.5

def high_leverage(de, sector):
    return de is not None and de > 5 and sector != "Financials"

def net_debt(borrowings, investments):
    return borrowings - investments

def asset_turnover(sales, assets):
    return None if assets == 0 else sales / assets