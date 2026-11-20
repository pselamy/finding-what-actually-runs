def compact(rows):
    latest = {}
    for row in rows:
        latest[row["coupon"]] = row
    return list(latest.values())
