def totals_by_segment(rows):
    totals = {}
    for row in rows:
        group = row["segment"]
        totals[group] = totals.get(group, 0) + row["cash"]
    return totals
