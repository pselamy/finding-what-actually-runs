def by_collection(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["collection"], []).append(row)
    return grouped
