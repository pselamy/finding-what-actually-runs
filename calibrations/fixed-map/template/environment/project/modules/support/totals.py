def totals_by_queue(rows):
    totals = {}
    for row in rows:
        group = row["queue"]
        totals[group] = totals.get(group, 0) + row["tickets"]
    return totals
