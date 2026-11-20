def by_region(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["region"], []).append(row)
    return grouped
