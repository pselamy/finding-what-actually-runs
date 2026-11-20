def totals_by_carrier(rows):
    totals = {}
    for row in rows:
        group = row["carrier"]
        totals[group] = totals.get(group, 0) + row["weight"]
    return totals
