import json


def assemble_fragments(fragments: list[str]) -> str:
    parsed_fragments = [
        json.loads(fragment)
        for fragment in fragments
    ]

    if not parsed_fragments:
        raise ValueError("No fragments provided.")

    transfer_id = parsed_fragments[0]["transfer_id"]
    expected_total = parsed_fragments[0]["fragment_total"]

    for fragment in parsed_fragments:
        if fragment["transfer_id"] != transfer_id:
            raise ValueError("Fragments belong to different transfers.")

        if fragment["fragment_total"] != expected_total:
            raise ValueError("Fragment totals do not match.")

    received_indexes = {
        fragment["fragment_index"]
        for fragment in parsed_fragments
    }

    expected_indexes = set(
        range(1, expected_total + 1)
    )

    missing_indexes = expected_indexes - received_indexes

    if missing_indexes:
        raise ValueError(
            f"Missing fragments: {sorted(missing_indexes)}"
        )

    parsed_fragments.sort(
        key=lambda fragment: fragment["fragment_index"]
    )

    packet_json = "".join(
        fragment["payload"]
        for fragment in parsed_fragments
    )

    return packet_json