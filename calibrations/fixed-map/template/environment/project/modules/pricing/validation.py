def normalized_key(row):
    return str(row["tier"]).strip().casefold()


def is_valid(row):
    return bool(normalized_key(row)) and isinstance(row.get("rate"), (float, int))
