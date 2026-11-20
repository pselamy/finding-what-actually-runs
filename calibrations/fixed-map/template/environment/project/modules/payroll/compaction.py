def compact(rows):
    latest = {}
    for row in rows:
        latest[row["payment"]] = row
    return list(latest.values())
