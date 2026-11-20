def compact(rows):
    latest = {}
    for row in rows:
        latest[row["contract"]] = row
    return list(latest.values())
