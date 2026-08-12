from datetime import datetime, timedelta
from sqlalchemy import func
from .models import db, WorkItem

ACTIVE_STATUSES = ("New", "Planned", "In Progress", "Blocked", "Waiting")
CLOSED_STATUSES = ("Completed", "Cancelled")

def _dict_rows(rows):
    return {str(k or "Uncategorized"): int(v) for k, v in rows}

def dashboard_data():
    counts = _dict_rows(
        db.session.query(WorkItem.status, func.count(WorkItem.id))
        .group_by(WorkItem.status).all()
    )
    priority = _dict_rows(
        db.session.query(WorkItem.priority, func.count(WorkItem.id))
        .group_by(WorkItem.priority).all()
    )
    category = _dict_rows(
        db.session.query(WorkItem.category, func.count(WorkItem.id))
        .group_by(WorkItem.category).all()
    )
    total = WorkItem.query.count()
    completed = counts.get("Completed", 0)
    return {
        "counts": counts,
        "priority": priority,
        "category": category,
        "total": total,
        "completed": completed,
        "completion_rate": round((completed / total * 100), 1) if total else 0,
    }

def management_analytics():
    now = datetime.utcnow()
    items = WorkItem.query.all()
    total = len(items)
    completed = sum(1 for i in items if i.status == "Completed")
    active = [i for i in items if i.status in ACTIVE_STATUSES]
    blocked = [i for i in items if i.status == "Blocked"]
    in_progress = [i for i in items if i.status == "In Progress"]
    waiting = [i for i in items if i.status == "Waiting"]

    avg_progress = round(
        sum((i.progress_percent or 0) for i in active) / len(active), 1
    ) if active else 0.0

    stale_30 = [
        i for i in active
        if i.created_date and i.created_date < (now - timedelta(days=30))
    ]
    stale_60 = [
        i for i in active
        if i.created_date and i.created_date < (now - timedelta(days=60))
    ]

    high_open = [
        i for i in active if (i.priority or "").lower() in ("high", "critical")
    ]

    # Category rollup for management view.
    categories = {}
    for item in items:
        key = item.category or "Uncategorized"
        rec = categories.setdefault(key, {
            "category": key, "total": 0, "completed": 0, "open": 0,
            "blocked": 0, "progress_sum": 0, "progress_n": 0
        })
        rec["total"] += 1
        if item.status == "Completed":
            rec["completed"] += 1
        elif item.status not in CLOSED_STATUSES:
            rec["open"] += 1
        if item.status == "Blocked":
            rec["blocked"] += 1
        if item.status not in CLOSED_STATUSES:
            rec["progress_sum"] += item.progress_percent or 0
            rec["progress_n"] += 1

    category_rows = []
    for rec in categories.values():
        rec["avg_progress"] = round(
            rec["progress_sum"] / rec["progress_n"], 1
        ) if rec["progress_n"] else (100.0 if rec["completed"] else 0.0)
        rec["completion_rate"] = round(
            rec["completed"] / rec["total"] * 100, 1
        ) if rec["total"] else 0.0
        category_rows.append(rec)
    category_rows.sort(key=lambda x: (-x["open"], x["category"].lower()))

    status_order = ["New","Planned","In Progress","Blocked","Waiting","Completed","Deferred","Cancelled"]
    counts = {s: 0 for s in status_order}
    for i in items:
        counts[i.status or "New"] = counts.get(i.status or "New", 0) + 1
    chart = [{"label": s, "value": counts.get(s, 0)} for s in status_order if counts.get(s, 0)]

    # Operational health score: transparent heuristic, not a hidden "AI" score.
    completion_rate = (completed / total * 100) if total else 0
    block_penalty = min(30, len(blocked) * 7.5)
    stale_penalty = min(25, len(stale_30) * 3)
    health = round(max(0, min(100, completion_rate * 0.55 + avg_progress * 0.45 - block_penalty - stale_penalty)), 1)

    return {
        "total": total,
        "completed": completed,
        "active_count": len(active),
        "in_progress_count": len(in_progress),
        "blocked_count": len(blocked),
        "waiting_count": len(waiting),
        "high_open_count": len(high_open),
        "stale_30_count": len(stale_30),
        "stale_60_count": len(stale_60),
        "avg_progress": avg_progress,
        "completion_rate": round(completion_rate, 1),
        "health_score": health,
        "categories": category_rows,
        "status_chart": chart,
        "blocked_items": sorted(blocked, key=lambda x: (x.priority != "Critical", x.title.lower()))[:10],
        "high_open_items": sorted(high_open, key=lambda x: (x.priority != "Critical", x.title.lower()))[:10],
    }
