from pathlib import Path
import tempfile
import os
import shutil
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response, current_app
from .models import db, WorkItem, ImportBatch, WorkHistory, AppSetting, WorkNote
from .import_engine import parse_upload
from .normalizer import find_duplicate
from .analytics import dashboard_data, management_analytics
from .reports import management_markdown
from .version import __version__
from .updater import stage_update, list_update_backups

bp = Blueprint("main", __name__)

@bp.app_context_processor
def inject_version(): return {"app_version": __version__}

@bp.route("/")
@bp.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=dashboard_data(),
                           recent=WorkItem.query.order_by(WorkItem.created_date.desc()).limit(8).all())

@bp.route("/work")
def work():
    q = WorkItem.query
    status = request.args.get("status")
    if status: q=q.filter_by(status=status)
    return render_template("work.html", items=q.order_by(WorkItem.id.desc()).all())

@bp.route("/work/new", methods=["GET","POST"])
def work_new():
    if request.method=="POST":
        item=WorkItem(title=request.form["title"].strip(), description=request.form.get("description",""),
                      category=request.form.get("category",""), work_type=request.form.get("work_type","TASK"),
                      priority=request.form.get("priority","Medium"), status=request.form.get("status","New"),
                      owner=request.form.get("owner",""), progress_percent=int(request.form.get("progress_percent") or 0))
        db.session.add(item); db.session.flush()
        db.session.add(WorkHistory(work_item_id=item.id,event="Created",detail="Manual entry"))
        db.session.commit()
        return redirect(url_for("main.work_detail", item_id=item.id))
    return render_template("work_form.html", item=None)

@bp.route("/work/<int:item_id>", methods=["GET","POST"])
def work_detail(item_id):
    item = WorkItem.query.get_or_404(item_id)

    if request.method == "POST":
        old = (item.status, item.progress_percent)

        item.title = request.form["title"].strip()
        item.description = request.form.get("description", "")
        item.category = request.form.get("category", "")
        item.work_type = request.form.get("work_type", "TASK")
        item.priority = request.form.get("priority", "Medium")
        item.status = request.form.get("status", "New")
        item.owner = request.form.get("owner", "")
        item.progress_percent = max(0, min(100, int(request.form.get("progress_percent") or 0)))
        item.ticket = request.form.get("ticket", "")

        if item.status == "Completed" and not item.completed_date:
            item.completed_date = datetime.utcnow().date()

        if old != (item.status, item.progress_percent):
            db.session.add(
                WorkHistory(
                    work_item_id=item.id,
                    event="Progress updated",
                    detail=f"{old[0]} {old[1]}% -> {item.status} {item.progress_percent}%"
                )
            )

        db.session.add(
            WorkHistory(
                work_item_id=item.id,
                event="Work item details saved",
                detail=f"Owner: {item.owner or 'Unassigned'}"
            )
        )
        db.session.commit()
        flash("Work item details saved.", "success")
        return redirect(url_for("main.work_detail", item_id=item.id))

    return render_template("work_form.html", item=item)


@bp.route("/work/<int:item_id>/notes", methods=["POST"])
def add_work_note(item_id):
    item = WorkItem.query.get_or_404(item_id)
    note_body = (request.form.get("note_text") or "").strip()
    if not note_body:
        flash("Enter a note before saving the artifact.", "warning")
        return redirect(url_for("main.work_detail", item_id=item.id))

    note_owner = (request.form.get("note_owner") or "").strip() or item.owner or "Unassigned"
    note = WorkNote(
        work_item_id=item.id,
        owner=note_owner,
        body=note_body,
        created_at=datetime.utcnow()
    )
    db.session.add(note)
    db.session.flush()
    db.session.add(
        WorkHistory(
            work_item_id=item.id,
            event="Note artifact added",
            detail=(
                f"Artifact #{note.id} | Owner: {note_owner} | "
                f"Timestamp: {note.created_at:%Y-%m-%d %H:%M:%S} UTC"
            )
        )
    )
    db.session.commit()
    flash(f"Note artifact #{note.id} saved.", "success")

    # PRG clears the dedicated note form and prevents duplicate artifact posts.
    return redirect(url_for("main.work_detail", item_id=item.id))


@bp.route("/import", methods=["GET","POST"])
def import_file():
    if request.method=="POST":
        f=request.files.get("file")
        if not f or not f.filename:
            flash("Choose a CSV, XLSX, or Markdown file.","danger"); return redirect(request.url)
        try: doc=parse_upload(f)
        except Exception as e:
            flash(str(e),"danger"); return redirect(request.url)
        candidates=[]
        for c in doc.candidates:
            dup=find_duplicate(c)
            c.duplicate_of=dup.id if dup else None
            candidates.append(c.__dict__)
        session["preview"]={"filename":doc.title,"source_type":doc.source_type,
                            "raw_text":doc.raw_text[:500000],"candidates":candidates}
        return render_template("import_preview.html", preview=session["preview"])
    return render_template("import.html")

@bp.route("/import/commit", methods=["POST"])
def import_commit():
    p=session.get("preview")
    if not p: flash("No pending import preview.","warning"); return redirect(url_for("main.import_file"))
    selected=set(request.form.getlist("selected"))
    batch=ImportBatch(filename=p["filename"],source_type=p["source_type"],raw_text=p.get("raw_text",""),
                      detected=len(p["candidates"]))
    db.session.add(batch); db.session.flush()
    accepted=duplicates=0
    for idx,c in enumerate(p["candidates"]):
        if str(idx) not in selected: continue
        if c.get("duplicate_of"): duplicates+=1
        item=WorkItem(title=c["title"],description=c.get("description",""),category=c.get("category",""),
                      work_type=c.get("work_type","TASK"),priority=c.get("priority","Medium"),
                      status=c.get("status","New"),owner=c.get("owner",""),
                      progress_percent=c.get("progress_percent",0),source=p["filename"],
                      source_batch_id=batch.id,source_section=c.get("source_section",""),
                      source_text=c.get("source_text",""))
        db.session.add(item); db.session.flush()
        db.session.add(WorkHistory(work_item_id=item.id,event="Imported",
                                   detail=f"Batch {batch.id}: {p['filename']}"))
        accepted+=1
    batch.accepted=accepted; batch.rejected=batch.detected-accepted; batch.duplicates=duplicates
    db.session.commit(); session.pop("preview",None)
    flash(f"Imported {accepted} work items.","success")
    return redirect(url_for("main.work"))

@bp.route("/imports")
def imports():
    return render_template("imports.html", batches=ImportBatch.query.order_by(ImportBatch.id.desc()).all())

@bp.route("/reports")
def reports():
    return render_template("reports.html")

@bp.route("/reports/management.md")
def management_report():
    return Response(management_markdown(), mimetype="text/markdown",
                    headers={"Content-Disposition":"attachment; filename=workhound-management-report.md"})


@bp.route("/analytics")
def analytics():
    return render_template("analytics.html", a=management_analytics())

def _setting(key, default=""):
    row = AppSetting.query.filter_by(key=key).first()
    return row.value if row else default

def _set_setting(key, value):
    row = AppSetting.query.filter_by(key=key).first()
    if not row:
        row = AppSetting(key=key, value=value)
        db.session.add(row)
    else:
        row.value = value

@bp.route("/setup", methods=["GET","POST"])
def setup():
    if request.method == "POST":
        action = request.form.get("action", "save_settings")

        if action == "save_settings":
            _set_setting("app_name", request.form.get("app_name","WorkHound").strip() or "WorkHound")
            _set_setting("default_owner", request.form.get("default_owner","").strip())
            _set_setting("report_org", request.form.get("report_org","").strip())
            _set_setting("update_channel", request.form.get("update_channel","stable").strip())
            db.session.commit()
            flash("Setup settings saved.", "success")
            return redirect(url_for("main.setup"))

        if action == "stage_update":
            upload = request.files.get("release_zip")
            if not upload or not upload.filename:
                flash("Choose a WorkHound release ZIP.", "danger")
                return redirect(url_for("main.setup"))
            if not upload.filename.lower().endswith(".zip"):
                flash("Release file must be a ZIP archive.", "danger")
                return redirect(url_for("main.setup"))

            tmpdir = Path(tempfile.mkdtemp(prefix="workhound-upload-"))
            tmpzip = tmpdir / "release.zip"
            try:
                upload.save(tmpzip)
                app_root = Path(current_app.root_path).parent.resolve()
                instance_path = Path(current_app.instance_path).resolve()
                result = stage_update(tmpzip, app_root, instance_path)
                flash(
                    f"WorkHound v{result.release_version} validated and staged. "
                    f"{result.files_updated} application files updated. "
                    f"Backup created: {result.backup_name}. Restart WorkHound to load the new release.",
                    "success"
                )
            except Exception as exc:
                flash(f"Update rejected: {exc}", "danger")
            finally:
                shutil.rmtree(tmpdir, ignore_errors=True)
            return redirect(url_for("main.setup"))

    settings = {
        "app_name": _setting("app_name", "WorkHound"),
        "default_owner": _setting("default_owner", ""),
        "report_org": _setting("report_org", ""),
        "update_channel": _setting("update_channel", "stable"),
    }
    backups = list_update_backups(Path(current_app.instance_path))
    marker_path = Path(current_app.instance_path) / "UPDATE_STAGED.txt"
    staged_update = marker_path.read_text(encoding="utf-8") if marker_path.exists() else ""
    return render_template(
        "setup.html",
        settings=settings,
        backups=backups,
        staged_update=staged_update,
        instance_path=current_app.instance_path,
    )

@bp.route("/admin")
def admin():
    return redirect(url_for("main.setup"))
