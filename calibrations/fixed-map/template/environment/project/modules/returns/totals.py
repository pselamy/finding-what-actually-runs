def totals_by_reason(rows):
    totals = {}
    for row in rows:
        group = row["reason"]
        totals[group] = totals.get(group, 0) + row["quantity"]
    return totals
