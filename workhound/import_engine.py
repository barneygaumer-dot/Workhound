from pathlib import Path
from .adapters.markdown_adapter import parse_markdown
from .adapters.csv_adapter import parse_csv
from .adapters.xlsx_adapter import parse_xlsx

def parse_upload(file_storage):
    name = file_storage.filename or "upload"
    ext = Path(name).suffix.lower()
    data = file_storage.read()
    if ext in (".md",".markdown"):
        return parse_markdown(data.decode("utf-8", errors="replace"), name)
    if ext == ".csv":
        return parse_csv(data.decode("utf-8-sig", errors="replace"), name)
    if ext == ".xlsx":
        return parse_xlsx(data, name)
    raise ValueError("Unsupported file type. Use CSV, XLSX, or Markdown.")
