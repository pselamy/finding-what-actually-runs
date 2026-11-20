def totals_by_campaign(rows):
    totals = {}
    for row in rows:
        group = row["campaign"]
        totals[group] = totals.get(group, 0) + row["uses"]
    return totals
