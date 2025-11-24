import os
import subprocess
from pathlib import Path


def split_flag(flag: str, parts: int) -> list[str]:
    """Разбить флаг на указанное количество частей."""
    length = len(flag)
    base, extra = divmod(length, parts)
    chunks: list[str] = []
    start = 0

    for i in range(parts):
        size = base + (1 if i < extra else 0)
        end = start + size
        chunks.append(flag[start:end])
        start = end

    return chunks


def main() -> None:
    flag = os.getenv("FLAG")
    assert flag, "FLAG is not set"

    src = Path("src.jpg")
    assert src.exists(), "Base image src.jpg not found"

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_image = output_dir / "history.jpg"

    # Копируем исходное изображение, чтобы не трогать оригинал
    output_image.write_bytes(src.read_bytes())

    # Разбиваем флаг на 6 частей (по числу полей)
    parts = split_flag(flag, 6)

    # Поля:
    # 0 - Название (Title)
    # 1 - Описание (ImageDescription)
    # 2 - Авторы (Artist)
    # 3 - Комментарий (UserComment)
    # 4 - Авторские права (Copyright)
    # 5 - Камера (Model)
    cmd = [
        "exiftool",
        "-overwrite_original",
        f"-Title={parts[0]}",
        f"-ImageDescription={parts[1]}",
        f"-Artist={parts[2]}",
        f"-UserComment={parts[3]}",
        f"-Copyright={parts[4]}",
        f"-Model={parts[5]}",
        str(output_image),
    ]

    subprocess.run(cmd, check=True)


if __name__ == "__main__":
    main()


