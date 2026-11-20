def totals_by_region(rows):
    totals = {}
    for row in rows:
        group = row["region"]
        totals[group] = totals.get(group, 0) + row["samples"]
    return totals
