import re
from .base import ImportedDocument, WorkCandidate

ACTION = re.compile(r"^(validate|review|create|align|socialize|improve|run|develop|verify|recommend|reduce|build|update|test|import|identify|generate|increase|eliminate|prevent)\b", re.I)

def parse_markdown(text, filename):
    doc = ImportedDocument(source_type="markdown", title=filename, raw_text=text)
    path = []
    current = None
    bullets = []
    key_counter = 0

    def flush():
        nonlocal current, bullets
        if current:
            current.description = "\n".join(bullets).strip()
            current.source_text = current.title + ("\n" + current.description if current.description else "")
            doc.candidates.append(current)
        current, bullets = None, []

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush()
            level = len(m.group(1))
            title = re.sub(r"^\d+\.\s*", "", m.group(2)).strip()
            path = path[:level-1] + [title]
            # H3+ headings and action-oriented headings are work candidates.
            if level >= 3 or ACTION.search(title):
                key_counter += 1
                category = path[-2] if len(path) > 1 else ""
                priority = "High" if "high priority" in " / ".join(path).lower() else "Medium"
                current = WorkCandidate(
                    title=title, category=category, priority=priority,
                    source_section=" > ".join(path[:-1]),
                    key=f"md-{key_counter}",
                    confidence=0.96 if ACTION.search(title) else 0.82
                )
            continue
        if current and re.match(r"^[-*]\s+", line):
            bullets.append(re.sub(r"^[-*]\s+", "", line))
        elif current and not line.startswith("**"):
            bullets.append(line)
    flush()
    return doc
