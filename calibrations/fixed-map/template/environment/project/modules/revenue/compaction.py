def compact(rows):
    latest = {}
    for row in rows:
        latest[row["receipt"]] = row
    return list(latest.values())
