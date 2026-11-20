def overlay(current, fields):
    return {name: fields.get(name, current[name]) for name in ("title", "body")}


def replace(current, fields):
    return overlay(current, fields)
