def totals_by_paygroup(rows):
    totals = {}
    for row in rows:
        group = row["paygroup"]
        totals[group] = totals.get(group, 0) + row["hours"]
    return totals
