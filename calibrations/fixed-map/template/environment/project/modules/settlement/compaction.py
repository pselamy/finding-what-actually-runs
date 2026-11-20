def compact(rows):
    latest = {}
    for row in rows:
        latest[row["batch"]] = row
    return list(latest.values())
