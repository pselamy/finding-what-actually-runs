def by_queue(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["queue"], []).append(row)
    return grouped
