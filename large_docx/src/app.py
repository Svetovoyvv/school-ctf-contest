import os
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET


CONTENT_TYPES_PATH = "[Content_Types].xml"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"


def main() -> None:
    flag = os.getenv("FLAG")
    assert flag, "FLAG is not set"

    template = Path("src.docx")
    assert template.exists(), "Template DOCX not found"

    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_docx = output_dir / "challenge.docx"

    # Repack DOCX as ZIP archive while adding flag.txt
    # Используем сжатие, чтобы строка флага не лежала в явном виде в архиве
    with ZipFile(template, "r") as zin, ZipFile(output_docx, "w", compression=ZIP_DEFLATED) as zout:
        # Copy all original files, but поправим [Content_Types].xml
        for item in zin.infolist():
            data = zin.read(item.filename)

            if item.filename == CONTENT_TYPES_PATH:
                # Добавляем описание для расширения .txt,
                # чтобы Word не считал документ повреждённым
                root = ET.fromstring(data)
                default_tag = f"{{{CT_NS}}}Default"

                has_txt = any(
                    el.get("Extension") == "txt"
                    for el in root.findall(default_tag)
                )
                if not has_txt:
                    el = ET.Element(default_tag)
                    el.set("Extension", "txt")
                    el.set("ContentType", "text/plain")
                    root.append(el)

                data = ET.tostring(root, encoding="utf-8", xml_declaration=True)

            # Перепаковываем с тем же именем, но уже с сжатием
            zout.writestr(item, data)

        # Add flag.txt with the flag value inside the DOCX archive
        # Кладём его в папку word/, чтобы структура была ближе к стандартной
        # и сохраняем только в сжатом виде (ZIP_DEFLATED), чтобы strings по challenge.docx
        # не показывал содержимое флага.
        zout.writestr("word/info.txt", flag.encode("utf-8"))


if __name__ == "__main__":
    main()

