from desk_normalize import expand, keep
from desk_persist import overlay, replace


def save(current, fields, layout):
    if layout == "imported":
        return overlay(current, expand(fields))
    return replace(current, keep(fields))
