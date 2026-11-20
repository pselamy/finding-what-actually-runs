def by_scenario(rows):
    grouped = {}
    for row in rows:
        grouped.setdefault(row["scenario"], []).append(row)
    return grouped
