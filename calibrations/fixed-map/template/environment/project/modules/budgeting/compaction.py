def compact(rows):
    latest = {}
    for row in rows:
        latest[row["envelope"]] = row
    return list(latest.values())
