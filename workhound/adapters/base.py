from dataclasses import dataclass, field

@dataclass
class WorkCandidate:
    title: str
    description: str = ""
    category: str = ""
    work_type: str = "TASK"
    priority: str = "Medium"
    owner: str = ""
    status: str = "New"
    progress_percent: int = 0
    source_section: str = ""
    source_text: str = ""
    parent_key: str | None = None
    key: str | None = None
    confidence: float = 1.0
    duplicate_of: int | None = None

@dataclass
class ImportedDocument:
    source_type: str
    title: str
    metadata: dict = field(default_factory=dict)
    candidates: list[WorkCandidate] = field(default_factory=list)
    raw_text: str = ""
