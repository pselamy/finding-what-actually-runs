def totals_by_warehouse(rows):
    totals = {}
    for row in rows:
        group = row["warehouse"]
        totals[group] = totals.get(group, 0) + row["units"]
    return totals
