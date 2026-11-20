def by_reason(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["reason"], []).append(row)
    return grouped
