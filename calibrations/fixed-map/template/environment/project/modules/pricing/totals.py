def totals_by_channel(rows):
    totals = {}
    for row in rows:
        group = row["channel"]
        totals[group] = totals.get(group, 0) + row["rate"]
    return totals
