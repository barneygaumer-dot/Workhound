import csv, io
from .base import ImportedDocument, WorkCandidate

ALIASES = {
    "title": ["title","item","objective","task","work item","work_item"],
    "description": ["description","details","detail"],
    "owner": ["owner","assigned to","assignee"],
    "priority": ["priority"],
    "status": ["status","state"],
    "notes": ["notes","comments"],
    "category": ["category","initiative","group"],
    "progress_percent": ["progress","progress percent","percent complete","% complete"],
}

def _map(headers):
    normalized = {h.strip().lower(): h for h in headers if h}
    out = {}
    for field, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                out[field] = normalized[alias]
                break
    return out

def parse_csv(text, filename):
    reader = csv.DictReader(io.StringIO(text))
    mapping = _map(reader.fieldnames or [])
    doc = ImportedDocument(source_type="csv", title=filename, raw_text=text,
                           metadata={"mapping": mapping})
    title_col = mapping.get("title")
    if not title_col:
        return doc
    for i, row in enumerate(reader, 1):
        title = (row.get(title_col) or "").strip()
        if not title: continue
        p = row.get(mapping.get("progress_percent",""), "0") or "0"
        try: p = int(float(str(p).replace("%","").strip()))
        except: p = 0
        doc.candidates.append(WorkCandidate(
            title=title,
            description=(row.get(mapping.get("description",""),"") or row.get(mapping.get("notes",""),"") or "").strip(),
            owner=(row.get(mapping.get("owner",""),"") or "").strip(),
            priority=(row.get(mapping.get("priority",""),"") or "Medium").strip(),
            status=(row.get(mapping.get("status",""),"") or "New").strip(),
            category=(row.get(mapping.get("category",""),"") or "").strip(),
            progress_percent=max(0,min(100,p)),
            source_section=f"row {i+1}",
            source_text=str(row),
            key=f"csv-{i}"
        ))
    return doc
