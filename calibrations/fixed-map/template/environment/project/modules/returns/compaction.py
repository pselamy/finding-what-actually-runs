def compact(rows):
    latest = {}
    for row in rows:
        latest[row["return"]] = row
    return list(latest.values())
