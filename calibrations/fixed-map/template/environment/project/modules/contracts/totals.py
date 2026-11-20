def totals_by_customer(rows):
    totals = {}
    for row in rows:
        group = row["customer"]
        totals[group] = totals.get(group, 0) + row["seats"]
    return totals
