import uuid


def unique_id():
    return str(uuid.uuid4()).split("-")[-1]
