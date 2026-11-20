def by_customer(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["customer"], []).append(row)
    return grouped
