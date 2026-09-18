import sqlite3
import re
from pathlib import Path

import pandas as pd

DB = "nifty100.db"
OUT = Path("output")
OUT.mkdir(exist_ok=True)


def year_num(x):
    m = re.search(r"(20\d{2})", str(x))
    return int(m.group(1)) if m else 0


def num(x):
    return pd.to_numeric(x, errors="coerce")


def conf_above(value, threshold, scale=2):
    if pd.isna(value):
        return 0
    return min(100, int(65 + max(0, value - threshold) * scale))


def conf_below(value, threshold, scale=3):
    if pd.isna(value):
        return 0
    return min(100, int(65 + max(0, threshold - value) * scale))


def add(rows, company, kind, rule, text, confidence):
    if confidence > 60:
        rows.append({
            "company_id": company,
            "type": kind,
            "rule_id": rule,
            "text": text,
            "confidence_pct": min(100, int(confidence))
        })


def increasing(values):
    v = [x for x in values if pd.notna(x)]
    return len(v) >= 3 and v[-3] < v[-2] < v[-1]


def decreasing(values):
    v = [x for x in values if pd.notna(x)]
    return len(v) >= 3 and v[-3] > v[-2] > v[-1]


def generate():
    with sqlite3.connect(DB) as conn:
        companies = pd.read_sql("SELECT * FROM companies", conn)
        sectors = pd.read_sql("SELECT * FROM sectors", conn)
        ratios = pd.read_sql("SELECT * FROM financial_ratios", conn)
        pl = pd.read_sql("SELECT * FROM profitandloss", conn)
        bs = pd.read_sql("SELECT * FROM balancesheet", conn)

    for df in [ratios, pl, bs]:
        df["year_num"] = df["year"].apply(year_num)

    rows = []

    for company in companies["id"].astype(str):
        r = ratios[ratios["company_id"] == company].sort_values("year_num")
        p = pl[pl["company_id"] == company].sort_values("year_num")
        b = bs[bs["company_id"] == company].sort_values("year_num")

        if r.empty:
            continue

        latest = r.iloc[-1]

        sector_row = sectors[sectors["company_id"] == company]
        sector = (
            str(sector_row.iloc[0]["broad_sector"])
            if not sector_row.empty else ""
        )

        is_financial = any(
            word in sector.lower()
            for word in ["financial", "bank", "insurance", "finance"]
        )

        roe = num(latest.get("return_on_equity_pct"))
        roce = num(latest.get("return_on_capital_pct"))
        de = num(latest.get("debt_to_equity"))
        icr = num(latest.get("interest_coverage"))
        fcf = num(latest.get("free_cash_flow_cr"))
        rev5 = num(latest.get("revenue_cagr_5yr"))
        pat5 = num(latest.get("pat_cagr_5yr"))
        eps5 = num(latest.get("eps_cagr_5yr"))
        opm = num(latest.get("operating_profit_margin_pct"))
        div_yield = num(latest.get("dividend_yield_pct"))
        payout = num(latest.get("dividend_payout_ratio_pct"))
        net_debt_ebitda = num(latest.get("net_debt_to_ebitda"))

        roe_hist = list(map(num, r["return_on_equity_pct"]))
        fcf_hist = list(map(num, r["free_cash_flow_cr"]))
        opm_hist = list(map(num, r["operating_profit_margin_pct"]))
        de_hist = list(map(num, r["debt_to_equity"]))
        eps_hist = list(map(num, r["earnings_per_share"]))

        # ---------------- PRO RULES ----------------

        # P1 ROE > 20% for 3+ years
        if len(roe_hist) >= 3 and all(
            pd.notna(x) and x > 20 for x in roe_hist[-3:]
        ):
            add(rows, company, "pro", "P1",
                "Consistently high return on equity above 20% demonstrates exceptional capital efficiency",
                conf_above(min(roe_hist[-3:]), 20))

        # P2 FCF positive for 5 years
        if len(fcf_hist) >= 5 and all(
            pd.notna(x) and x > 0 for x in fcf_hist[-5:]
        ):
            add(rows, company, "pro", "P2",
                "Strong free cash flow generation over 5 years signals healthy business fundamentals",
                85)

        # P3 Debt free
        if pd.notna(de) and de == 0:
            add(rows, company, "pro", "P3",
                "Debt-free balance sheet provides financial flexibility and eliminates interest burden",
                95)

        # P4 Revenue CAGR > 15%
        if pd.notna(rev5) and rev5 > 15:
            add(rows, company, "pro", "P4",
                "Revenue growing at above 15% CAGR over 5 years reflects strong business momentum",
                conf_above(rev5, 15))

        # P5 OPM > 25%
        if pd.notna(opm) and opm > 25:
            add(rows, company, "pro", "P5",
                "Operating profit margin above 25% indicates strong pricing power and cost discipline",
                conf_above(opm, 25))

        # P6 PAT CAGR > 20%
        if pd.notna(pat5) and pat5 > 20:
            add(rows, company, "pro", "P6",
                "Net profit compounding at above 20% over 5 years creates significant shareholder value",
                conf_above(pat5, 20))

        # P7 ICR > 10 or debt free
        if (pd.notna(icr) and icr > 10) or (pd.notna(de) and de == 0):
            add(rows, company, "pro", "P7",
                "Very high interest coverage ratio reflects negligible financial stress from debt servicing",
                85 if pd.isna(icr) else conf_above(icr, 10))

        # P8 Dividend Yield > 2 and FCF positive
        if (
            pd.notna(div_yield) and div_yield > 2
            and pd.notna(fcf) and fcf > 0
        ):
            add(rows, company, "pro", "P8",
                "Consistent dividend yield above 2% backed by positive free cash flow",
                conf_above(div_yield, 2, 5))

        # P9 EPS CAGR > 15%
        if pd.notna(eps5) and eps5 > 15:
            add(rows, company, "pro", "P9",
                "Earnings per share growing above 15% CAGR indicates strong earnings quality and compounding",
                conf_above(eps5, 15))

        # P10 ROE improving 3 years
        if increasing(roe_hist):
            add(rows, company, "pro", "P10",
                "Return on equity improving for 3 consecutive years shows strengthening business quality",
                80)

        # P11 PAT growing faster than revenue
        if (
            pd.notna(rev5) and pd.notna(pat5)
            and pat5 > rev5
        ):
            add(rows, company, "pro", "P11",
                "Revenue growing slower than profits shows improving operating leverage and scale benefits",
                min(100, 70 + int(pat5 - rev5)))

        # P12 Assets rising and debt declining
        if len(b) >= 2:
            prev_b, curr_b = b.iloc[-2], b.iloc[-1]

            prev_assets = num(prev_b["total_assets"])
            curr_assets = num(curr_b["total_assets"])
            prev_debt = num(prev_b["borrowings"])
            curr_debt = num(curr_b["borrowings"])

            if (
                pd.notna(prev_assets) and pd.notna(curr_assets)
                and pd.notna(prev_debt) and pd.notna(curr_debt)
                and curr_assets > prev_assets
                and curr_debt < prev_debt
            ):
                add(rows, company, "pro", "P12",
                    "Growing asset base funded by internal accruals reflects self-sustaining growth",
                    80)

        # ---------------- CON RULES ----------------

        # C1 D/E > 2 non-financial
        if not is_financial and pd.notna(de) and de > 2:
            add(rows, company, "con", "C1",
                f"Debt-to-equity ratio of {de:.2f} is elevated for a non-financial company and warrants monitoring",
                conf_above(de, 2, 8))

        # C2 FCF negative 3 years
        if len(fcf_hist) >= 3 and all(
            pd.notna(x) and x < 0 for x in fcf_hist[-3:]
        ):
            add(rows, company, "con", "C2",
                "Free cash flow negative for 3 consecutive years raises concern about cash generation quality",
                90)

        # C3 OPM declining 3 years
        if decreasing(opm_hist):
            add(rows, company, "con", "C3",
                "Operating margins declining for 3 consecutive years suggest pricing or cost pressure",
                80)

        # C4 Net profit negative
        if not p.empty:
            net_profit = num(p.iloc[-1]["net_profit"])

            if pd.notna(net_profit) and net_profit < 0:
                add(rows, company, "con", "C4",
                    "Company reported a net loss in the most recent financial year",
                    95)

        # C5 Revenue declining 2+ consecutive years
        if len(p) >= 3:
            sales = list(map(num, p["sales"]))

            if decreasing(sales):
                add(rows, company, "con", "C5",
                    "Revenue contraction over 2 consecutive years indicates demand weakness or market share loss",
                    85)

        # C6 ICR < 1.5
        if pd.notna(icr) and icr < 1.5:
            add(rows, company, "con", "C6",
                "Interest coverage ratio below 1.5x indicates the company is at risk of not meeting its debt obligations",
                conf_below(icr, 1.5, 15))

        # C7 Dividend payout > 100%
        if pd.notna(payout) and payout > 100:
            add(rows, company, "con", "C7",
                "Dividend payout ratio above 100% means the company is paying dividends from reserves, which is unsustainable",
                conf_above(payout, 100, 1))

        # C8 D/E rising 3 years
        if increasing(de_hist):
            add(rows, company, "con", "C8",
                "Rising debt-to-equity ratio over 3 years suggests increasing financial leverage risk",
                80)

        # C9 EPS declining 3 years
        if decreasing(eps_hist):
            add(rows, company, "con", "C9",
                "Earnings per share declining for 3 consecutive years reflects deteriorating profitability",
                80)

        # C10 ROCE < 10%
        if pd.notna(roce) and roce < 10:
            add(rows, company, "con", "C10",
                "Return on capital employed below 10% suggests the business is not generating sufficient returns on invested capital",
                conf_below(roce, 10))

        # C11 Net Debt > 3x EBITDA
        if pd.notna(net_debt_ebitda) and net_debt_ebitda > 3:
            add(rows, company, "con", "C11",
                "Net debt exceeding 3 times EBITDA is a high leverage ratio and limits financial flexibility",
                conf_above(net_debt_ebitda, 3, 5))

        # C12 Revenue CAGR < 5%
        if pd.notna(rev5) and rev5 < 5:
            add(rows, company, "con", "C12",
                "Revenue growing at below 5% over 5 years lags inflation and suggests limited business momentum",
                conf_below(rev5, 5, 3))

    result = pd.DataFrame(rows)
    result.to_csv(OUT / "pros_cons_generated.csv", index=False)

    # Verification
    company_ids = set(companies["id"].astype(str))

    pros = set(result[result["type"] == "pro"]["company_id"])
    cons = set(result[result["type"] == "con"]["company_id"])

    missing_pro = sorted(company_ids - pros)
    missing_con = sorted(company_ids - cons)

    print("Generated rows:", len(result))
    print("Companies:", len(company_ids))
    print("Companies with Pro:", len(pros))
    print("Companies with Con:", len(cons))

    print("\nMissing Pro:", missing_pro)
    print("Missing Con:", missing_con)

    if not missing_pro and not missing_con:
        print("\nDay 30 verification: PASSED")
    else:
        print("\nDay 30 verification: PARTIAL")
        print("Reason: some companies did not trigger any qualifying Pro/Con rule.")

    print("\nCreated:")
    print("output/pros_cons_generated.csv")

if __name__ == "__main__":
    generate()