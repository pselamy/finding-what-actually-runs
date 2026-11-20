def by_group(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["group"], []).append(row)
    return grouped
