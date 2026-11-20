def normalized_key(row):
    return str(row["sku"]).strip().casefold()


def is_valid(row):
    return bool(normalized_key(row)) and isinstance(row.get("stock"), (float, int))
