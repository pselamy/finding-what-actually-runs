def compact(rows):
    latest = {}
    for row in rows:
        latest[row["shipment"]] = row
    return list(latest.values())
