def by_paygroup(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["paygroup"], []).append(row)
    return grouped
