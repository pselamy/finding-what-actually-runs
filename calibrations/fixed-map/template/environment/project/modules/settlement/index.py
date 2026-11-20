def by_processor(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["processor"], []).append(row)
    return grouped
