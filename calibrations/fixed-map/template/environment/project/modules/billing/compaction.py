def compact(rows):
    latest = {}
    for row in rows:
        latest[row["invoice"]] = row
    return list(latest.values())
