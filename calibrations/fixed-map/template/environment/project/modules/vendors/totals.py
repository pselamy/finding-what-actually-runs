def totals_by_category(rows):
    totals = {}
    for row in rows:
        group = row["category"]
        totals[group] = totals.get(group, 0) + row["quotations"]
    return totals
