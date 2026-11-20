def compact(rows):
    latest = {}
    for row in rows:
        latest[row["service"]] = row
    return list(latest.values())
