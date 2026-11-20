def totals_by_account(rows):
    totals = {}
    for row in rows:
        group = row["account"]
        totals[group] = totals.get(group, 0) + row["charge"]
    return totals
