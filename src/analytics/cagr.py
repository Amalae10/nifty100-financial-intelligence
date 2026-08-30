def cagr(start,end,years):
    if years <=0:
        return None,"INSUFFICIENT"

    if start == 0:
        return None,"ZERO_BASE"

    if start > 0 and end < 0:
        return None,"DECLINE_TO_LOSS"

    if start < 0 and end > 0:
        return None,"TURNAROUND"

    if start < 0 and end < 0:
        return None,"BOTH_NEGATIVE"

    if start > 0 and end > 0:
        value =((end/start)**(1/years) -1) *100
        return value,"OK"

    return None,"INSUFFICIENT"