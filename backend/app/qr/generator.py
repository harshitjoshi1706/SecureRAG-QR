from pathlib import Path

import qrcode


QR_OUTPUT_DIR = Path("storage/qr")

QR_OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def generate_qr_codes(
    fragments: list[str],
    transfer_id: str
) -> list[str]:

    generated_files = []

    for index, fragment in enumerate(
        fragments,
        start=1
    ):

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=8,
            border=4
        )

        qr.add_data(fragment)

        qr.make(fit=True)

        image = qr.make_image(
            fill_color="black",
            back_color="white"
        )

        filename = (
            f"{transfer_id}_"
            f"{index}_of_{len(fragments)}.png"
        )

        file_path = QR_OUTPUT_DIR / filename

        image.save(file_path)

        generated_files.append(
            str(file_path)
        )

    return generated_files