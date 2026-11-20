def by_currency(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["currency"], []).append(row)
    return grouped
