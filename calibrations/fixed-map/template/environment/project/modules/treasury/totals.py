def totals_by_currency(rows):
    totals = {}
    for row in rows:
        group = row["currency"]
        totals[group] = totals.get(group, 0) + row["principal"]
    return totals
