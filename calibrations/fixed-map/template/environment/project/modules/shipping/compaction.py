def compact(rows):
    latest = {}
    for row in rows:
        latest[row["parcel"]] = row
    return list(latest.values())
