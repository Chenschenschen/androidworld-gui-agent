"""Read course materials without executing archive contents."""
from pathlib import Path
import hashlib
import json
import zipfile
from pypdf import PdfReader

root = Path(__file__).resolve().parent.parent
out = root / ".review" / "materials"
out.mkdir(parents=True, exist_ok=True)
inventory = []
for source in sorted((root / "course_content").iterdir()):
    record = {"source": source.name, "bytes": source.stat().st_size,
              "sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
    if source.suffix.lower() == ".pdf":
        reader = PdfReader(source)
        pages = [page.extract_text() or "" for page in reader.pages]
        record["pages"] = len(pages)
        record["empty_text_pages"] = [i+1 for i,t in enumerate(pages) if not t.strip()]
        target = out / (source.stem + ".txt")
        target.write_text("\n\n".join(f"=== PAGE {i+1} ===\n{text}" for i,text in enumerate(pages)), encoding="utf-8")
        record["text_chars"] = sum(map(len, pages))
    elif source.suffix.lower() == ".zip":
        entries = []
        with zipfile.ZipFile(source) as archive:
            for entry in archive.infolist():
                item = {"name": entry.filename, "bytes": entry.file_size}
                if not entry.is_dir():
                    data = archive.read(entry)
                    item["sha256"] = hashlib.sha256(data).hexdigest()
                    metadata = "__MACOSX" in entry.filename or entry.filename.endswith(".DS_Store")
                    item["kind"] = "macOS metadata" if metadata else "course content"
                    relative = Path(entry.filename)
                    target = (out / source.stem / relative).resolve()
                    if not target.is_relative_to(out.resolve()):
                        raise ValueError(f"Unsafe archive path: {entry.filename}")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    if not metadata:
                        data.decode("utf-8")
                entries.append(item)
        record["entries"] = entries
    inventory.append(record)
(out / "inventory.json").write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(inventory, ensure_ascii=False, indent=2))
