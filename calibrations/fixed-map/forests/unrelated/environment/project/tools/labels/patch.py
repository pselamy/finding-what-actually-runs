def patch(snapshot, fields):
    return {
        "label": fields.get("label", ""),
        "hint": fields.get("hint", ""),
    }
