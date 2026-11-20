def totals_by_scenario(rows):
    totals = {}
    for row in rows:
        group = row["scenario"]
        totals[group] = totals.get(group, 0) + row["estimate"]
    return totals
