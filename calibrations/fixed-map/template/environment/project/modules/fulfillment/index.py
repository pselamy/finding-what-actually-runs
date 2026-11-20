def by_warehouse(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["warehouse"], []).append(row)
    return grouped
