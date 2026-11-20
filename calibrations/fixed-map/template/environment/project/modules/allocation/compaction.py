def compact(rows):
    latest = {}
    for row in rows:
        latest[row["center"]] = row
    return list(latest.values())
