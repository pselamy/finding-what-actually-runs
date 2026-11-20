def totals_by_processor(rows):
    totals = {}
    for row in rows:
        group = row["processor"]
        totals[group] = totals.get(group, 0) + row["net"]
    return totals
