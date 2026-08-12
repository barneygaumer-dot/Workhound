from datetime import datetime
from .models import WorkItem
from .analytics import management_analytics

def management_markdown():
    a = management_analytics()
    items = WorkItem.query.order_by(WorkItem.priority, WorkItem.title).all()
    groups = {}
    for i in items:
        groups.setdefault(i.status or "Unknown", []).append(i)

    out = [
        "# WorkHound Management Progress Report",
        "",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## Executive Snapshot",
        "",
        f"- Total tracked work: **{a['total']}**",
        f"- Active work: **{a['active_count']}**",
        f"- In progress: **{a['in_progress_count']}**",
        f"- Blocked: **{a['blocked_count']}**",
        f"- Completed: **{a['completed']}**",
        f"- Completion rate: **{a['completion_rate']}%**",
        f"- Average active progress: **{a['avg_progress']}%**",
        f"- High/Critical open items: **{a['high_open_count']}**",
        f"- Active items older than 30 days: **{a['stale_30_count']}**",
        f"- Operational health score: **{a['health_score']}/100**",
        "",
        "## Initiative / Category Rollup",
        "",
        "| Initiative | Total | Open | Completed | Blocked | Avg Progress |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for c in a["categories"]:
        out.append(
            f"| {c['category']} | {c['total']} | {c['open']} | {c['completed']} | "
            f"{c['blocked']} | {c['avg_progress']}% |"
        )
    out.append("")

    for status in ["Completed","In Progress","Blocked","Waiting","Planned","New","Deferred","Cancelled"]:
        vals = groups.get(status, [])
        if not vals:
            continue
        out += [f"## {status} ({len(vals)})", ""]
        for i in vals:
            extra = f" — {i.progress_percent}%" if i.progress_percent else ""
            category = f" ({i.category})" if i.category else ""
            owner = f" — Owner: {i.owner}" if i.owner else ""
            out.append(f"- **{i.title}**{extra}{category}{owner}")
            if i.note_artifacts:
                latest = i.note_artifacts[0]
                note_owner = latest.owner or "Unassigned"
                note_body = " ".join((latest.body or "").split())
                if len(note_body) > 220:
                    note_body = note_body[:217] + "..."
                out.append(
                    f"  - Latest artifact #{latest.id} "
                    f"({latest.created_at:%Y-%m-%d %H:%M:%S} UTC, {note_owner}): {note_body}"
                )
            elif i.notes:
                legacy = " ".join(i.notes.split())
                if len(legacy) > 220:
                    legacy = legacy[:217] + "..."
                out.append(f"  - Legacy note: {legacy}")
        out.append("")
    return "\n".join(out)
