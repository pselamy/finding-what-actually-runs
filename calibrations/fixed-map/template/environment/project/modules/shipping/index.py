def by_carrier(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["carrier"], []).append(row)
    return grouped
