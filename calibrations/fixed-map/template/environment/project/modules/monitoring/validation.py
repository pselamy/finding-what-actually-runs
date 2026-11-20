def normalized_key(row):
    return str(row["service"]).strip().casefold()


def is_valid(row):
    return bool(normalized_key(row)) and isinstance(row.get("samples"), (float, int))
