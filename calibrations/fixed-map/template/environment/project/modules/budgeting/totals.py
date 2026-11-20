def totals_by_group(rows):
    totals = {}
    for row in rows:
        group = row["group"]
        totals[group] = totals.get(group, 0) + row["planned"]
    return totals
