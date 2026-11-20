def by_segment(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["segment"], []).append(row)
    return grouped
