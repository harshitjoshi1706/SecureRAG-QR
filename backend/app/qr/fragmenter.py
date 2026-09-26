import json


DEFAULT_FRAGMENT_SIZE = 800


def fragment_packet(
    packet_json: str,
    transfer_id: str,
    fragment_size: int = DEFAULT_FRAGMENT_SIZE
) -> list[str]:

    payload_parts = []

    for start in range(
        0,
        len(packet_json),
        fragment_size
    ):
        payload_parts.append(
            packet_json[start:start + fragment_size]
        )

    total_fragments = len(payload_parts)

    fragments = []

    for index, payload_part in enumerate(payload_parts):

        fragment = {
            "version": "SRQ1",
            "transfer_id": transfer_id,
            "fragment_index": index + 1,
            "fragment_total": total_fragments,
            "payload": payload_part
        }

        fragment_json = json.dumps(
            fragment,
            separators=(",", ":")
        )

        fragments.append(fragment_json)

    return fragments