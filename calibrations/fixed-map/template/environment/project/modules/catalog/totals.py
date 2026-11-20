def totals_by_collection(rows):
    totals = {}
    for row in rows:
        group = row["collection"]
        totals[group] = totals.get(group, 0) + row["stock"]
    return totals
