def compact(rows):
    latest = {}
    for row in rows:
        latest[row["case"]] = row
    return list(latest.values())
