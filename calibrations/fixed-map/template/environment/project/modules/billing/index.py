def by_account(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["account"], []).append(row)
    return grouped
