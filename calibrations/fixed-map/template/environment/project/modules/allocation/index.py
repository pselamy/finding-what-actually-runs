def by_department(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["department"], []).append(row)
    return grouped
