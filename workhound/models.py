from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ImportBatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    source_type = db.Column(db.String(32), nullable=False)
    imported_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    detected = db.Column(db.Integer, default=0)
    accepted = db.Column(db.Integer, default=0)
    rejected = db.Column(db.Integer, default=0)
    duplicates = db.Column(db.Integer, default=0)
    raw_text = db.Column(db.Text)

class WorkItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(120))
    work_type = db.Column(db.String(40), default="TASK")
    priority = db.Column(db.String(20), default="Medium")
    status = db.Column(db.String(30), default="New")
    owner = db.Column(db.String(120))
    stakeholder = db.Column(db.String(120))
    source = db.Column(db.String(255))
    source_batch_id = db.Column(db.Integer, db.ForeignKey("import_batch.id"))
    source_section = db.Column(db.String(500))
    source_text = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    target_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    progress_percent = db.Column(db.Integer, default=0)
    disposition = db.Column(db.String(200))
    notes = db.Column(db.Text)
    ticket = db.Column(db.String(100))
    external_reference = db.Column(db.String(500))
    parent_id = db.Column(db.Integer, db.ForeignKey("work_item.id"))
    parent = db.relationship("WorkItem", remote_side=[id], backref="children")
    batch = db.relationship("ImportBatch", backref="work_items")

class WorkHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_item_id = db.Column(db.Integer, db.ForeignKey("work_item.id"), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    event = db.Column(db.String(120), nullable=False)
    detail = db.Column(db.Text)
    item = db.relationship("WorkItem", backref=db.backref("history", cascade="all, delete-orphan"))


class AppSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(120), unique=True, nullable=False)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class WorkNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    work_item_id = db.Column(db.Integer, db.ForeignKey("work_item.id"), nullable=False, index=True)
    owner = db.Column(db.String(120))
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

    item = db.relationship(
        "WorkItem",
        backref=db.backref(
            "note_artifacts",
            cascade="all, delete-orphan",
            order_by="WorkNote.created_at.desc()"
        )
    )
