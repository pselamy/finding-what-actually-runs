def compact(rows):
    latest = {}
    for row in rows:
        latest[row["position"]] = row
    return list(latest.values())
