def compact(rows):
    latest = {}
    for row in rows:
        latest[row["sku"]] = row
    return list(latest.values())
