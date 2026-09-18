def fcf(cfo, cfi):
    return cfo + cfi


def cfo_quality(cfo_pat_ratios):
    vals = [x for x in cfo_pat_ratios if x is not None]

    if not vals:
        return None

    avg = sum(vals) / len(vals)

    if avg > 1:
        return "High Quality"
    if avg >= 0.5:
        return "Moderate"
    return "Accrual Risk"


def cfo_pat_ratio(cfo, pat):
    return None if pat == 0 else cfo / pat


def capex_intensity(cfi, sales):
    if sales == 0:
        return None

    pct = abs(cfi) / sales * 100

    if pct < 3:
        return "Asset Light"
    if pct <= 8:
        return "Moderate"
    return "Capital Intensive"


def fcf_conversion(fcf_value, op_profit):
    return None if op_profit == 0 else fcf_value / op_profit * 100


def allocation(cfo, cfi, cff, cfo_pat=None):
    signs = (
        "+" if cfo > 0 else "-",
        "+" if cfi > 0 else "-",
        "+" if cff > 0 else "-"
    )

    if signs == ("+", "-", "-"):
        if cfo_pat is not None and cfo_pat > 1:
            return signs, "Shareholder Returns"
        return signs, "Reinvestor"

    patterns = {
        ("+", "+", "-"): "Liquidating Assets",
        ("-", "+", "+"): "Distress Signal",
        ("-", "-", "+"): "Growth Funded by Debt",
        ("+", "+", "+"): "Cash Accumulator",
        ("-", "-", "-"): "Pre-Revenue",
        ("+", "-", "+"): "Mixed",
    }

    return signs, patterns.get(signs, "Mixed")

def distress_signal(cfo, cff):
    return cfo < 0 and cff > 0


def deleveraging(cff, current_borrowings, previous_borrowings):
    return (
        cff < 0
        and current_borrowings < previous_borrowings
    )