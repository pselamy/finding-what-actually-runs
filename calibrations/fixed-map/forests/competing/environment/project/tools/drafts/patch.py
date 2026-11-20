def patch(snapshot, fields):
    return {
        "title": fields.get("title", ""),
        "body": fields.get("body", ""),
    }
