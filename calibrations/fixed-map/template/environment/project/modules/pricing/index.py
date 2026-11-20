def by_channel(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["channel"], []).append(row)
    return grouped
