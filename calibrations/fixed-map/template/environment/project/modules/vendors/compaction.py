def compact(rows):
    latest = {}
    for row in rows:
        latest[row["vendor"]] = row
    return list(latest.values())
