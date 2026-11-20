def normalized_key(row):
    return str(row["center"]).strip().casefold()


def is_valid(row):
    return bool(normalized_key(row)) and isinstance(row.get("credit"), (float, int))
