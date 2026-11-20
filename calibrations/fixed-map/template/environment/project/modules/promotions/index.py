def by_campaign(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["campaign"], []).append(row)
    return grouped
