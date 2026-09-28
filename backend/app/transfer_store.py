transfer_store = {}


def save_transfer(transfer_id: str, data: dict):
    transfer_store[transfer_id] = data


def get_transfer(transfer_id: str):
    return transfer_store.get(transfer_id)