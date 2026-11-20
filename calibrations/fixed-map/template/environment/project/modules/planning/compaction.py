def compact(rows):
    latest = {}
    for row in rows:
        latest[row["forecast"]] = row
    return list(latest.values())
