import re
from difflib import SequenceMatcher
from .models import WorkItem

def normalized_title(s):
    return re.sub(r"[^a-z0-9]+"," ", (s or "").lower()).strip()

def find_duplicate(candidate):
    target = normalized_title(candidate.title)
    best = (0.0, None)
    for item in WorkItem.query.all():
        score = SequenceMatcher(None, target, normalized_title(item.title)).ratio()
        if score > best[0]:
            best = (score, item)
    return best[1] if best[0] >= 0.90 else None
