def compact(rows):
    latest = {}
    for row in rows:
        latest[row["tier"]] = row
    return list(latest.values())
