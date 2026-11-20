def totals_by_department(rows):
    totals = {}
    for row in rows:
        group = row["department"]
        totals[group] = totals.get(group, 0) + row["credit"]
    return totals
