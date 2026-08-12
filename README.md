# WorkHound

**Operational Work Intelligence**

WorkHound is a local-first web application for turning semi-structured work data into a durable operational work queue.

It ingests **CSV**, **XLSX**, and **Markdown**, normalizes supported fields into a canonical Work Item model, presents a preview before commit, preserves source evidence and import provenance, tracks execution and timestamped work-note artifacts, and provides dashboard, analytics, and management-report views.

> **WorkHound answers a simple operational question: _What work exists, what is moving, what is stuck, and what are we accomplishing?_**

Current release: **v0.1.3**

---

## Table of Contents

- [Why WorkHound](#why-workhound)
- [What WorkHound Does](#what-workhound-does)
- [Core Design Rule](#core-design-rule)
- [Features](#features)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Using WorkHound](#using-workhound)
- [Import Minimum Standards](#import-minimum-standards)
- [CSV and XLSX Import Contract](#csv-and-xlsx-import-contract)
- [Markdown Import Contract](#markdown-import-contract)
- [Import Examples](#import-examples)
- [Import Preview and Duplicate Detection](#import-preview-and-duplicate-detection)
- [Canonical Work Item Model](#canonical-work-item-model)
- [Work Note Artifacts](#work-note-artifacts)
- [Dashboard and Analytics](#dashboard-and-analytics)
- [Management Reporting](#management-reporting)
- [Import Batches and Provenance](#import-batches-and-provenance)
- [Setup and Administration](#setup-and-administration)
- [Updating WorkHound](#updating-workhound)
- [Data Storage and Backup](#data-storage-and-backup)
- [Security and Deployment Notes](#security-and-deployment-notes)
- [Troubleshooting Imports](#troubleshooting-imports)
- [Known Limitations](#known-limitations)
- [Project Structure](#project-structure)
- [Versioning](#versioning)
- [Contributing](#contributing)

---

## Why WorkHound

Operational work rarely arrives in one clean system.

It may be spread across:

- spreadsheets;
- exported reports;
- meeting notes;
- action-item lists;
- Copilot-generated summaries;
- engineering review documents;
- project trackers;
- manually maintained CSV files.

The problem is not merely storing those files. The problem is converting them into a consistent execution model without losing the evidence that produced the work.

WorkHound separates those concerns:

```text
Source Data
   |
   v
Format Adapter
   |
   v
Work Candidates
   |
   v
Preview + Duplicate Warning
   |
   v
User Approval
   |
   v
Canonical Work Items
   |
   +--> Execution Tracking
   +--> Timestamped Note Artifacts
   +--> History
   +--> Dashboard
   +--> Analytics
   +--> Management Reporting
```

The source format is allowed to vary. The internal work model does not have to.

---

## What WorkHound Does

WorkHound is intended to sit between **raw operational information** and **managed execution**.

A typical workflow is:

1. Receive or generate a CSV, XLSX, or Markdown document.
2. Upload it to WorkHound.
3. WorkHound parses the document into candidate Work Items.
4. Review the import preview.
5. Review possible duplicate warnings.
6. Select the candidates that should become real Work Items.
7. Commit the import.
8. Assign owners, priorities, statuses, progress, and tickets.
9. Add timestamped Work Note Artifacts as the work evolves.
10. Use Dashboard and Analytics to understand execution.
11. Export the management Markdown report when a portable status report is needed.

WorkHound does **not** require an external AI service to perform these functions. The v0.1.3 import and analytics behavior is deterministic and local.

---

## Core Design Rule

> **Imports do not define WorkHound's database schema. The WorkHound schema defines what imported information becomes.**

This is the central architectural rule.

CSV columns, spreadsheet layouts, and Markdown structures are treated as **source representations**. Adapters convert supported source information into intermediary `WorkCandidate` objects. Only candidates explicitly selected in the preview are committed as Work Items.

This keeps the operational data model stable even when source documents vary.

---

## Features

### Import and normalization

- CSV ingestion
- XLSX ingestion from the active worksheet
- Markdown structural/action-item extraction
- Common-column alias mapping
- UTF-8 / UTF-8 BOM handling for CSV and Markdown
- Import preview before commit
- Per-candidate selection
- Possible duplicate detection
- Import batch accounting
- Source filename, source section, and source evidence retention

### Work management

- Title
- Description
- Category / initiative
- Owner
- Work type
- Priority
- Status
- Progress percentage
- Ticket / work-order reference
- Created and completed dates
- Work history

### Work Note Artifacts

- Append-only operational notes
- Artifact ID
- Artifact owner
- Owner override per artifact
- UTC creation timestamp
- Independent **Save Note Artifact** transaction
- Independent **Save Work Item Details** transaction
- Legacy-note preservation

### Operational intelligence

- Dashboard metrics
- Work-by-status view
- Work-by-priority view
- Recent work
- Management Analytics tab
- Completion rate
- Average active progress
- Blocked and waiting counts
- High/Critical open-work counts
- 30-day and 60-day aging
- Initiative/category rollups
- Status graph
- Blocked-work drill-down
- High-priority work drill-down
- Deterministic operational-health heuristic

### Reporting and administration

- Downloadable Markdown management report
- Persistent application settings
- Import batch history
- Version reporting
- In-application **Update from Release ZIP**
- Pre-update backups
- ZIP validation and path-traversal protection
- Numeric WolfPack release validation

---

## Requirements

WorkHound v0.1.3 requires:

- Python 3
- `venv` support
- Flask 3.x
- Flask-SQLAlchemy 3.x
- openpyxl 3.x
- A modern web browser

Dependencies are declared in `requirements.txt`.

The application uses a local SQLite database by default.

---

## Quick Start

### Linux / macOS-style shell

```bash
unzip workhound-v0.1.3.zip
cd workhound-v0.1.3

python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python run.py --version
python run.py --host 127.0.0.1 --port 5000
```

Expected version output:

```text
0.1.3
```

Open:

```text
http://127.0.0.1:5000
```

To listen on all interfaces:

```bash
python run.py --host 0.0.0.0 --port 5000
```

See [Security and Deployment Notes](#security-and-deployment-notes) before exposing the development server beyond a trusted environment.

### Command-line options

```bash
python run.py --help
```

v0.1.3 supports:

```text
--host
--port
--debug
--version
```

---

# Using WorkHound

The main navigation surfaces are:

| Area | Purpose |
|---|---|
| **Dashboard** | Fast operational snapshot |
| **Work** | Browse and manage committed Work Items |
| **Analytics** | Management-oriented execution analytics |
| **Import** | Upload and preview CSV/XLSX/Markdown data |
| **Batches** | Review import history |
| **Reports** | Download management reporting |
| **Setup** | Application settings and release updates |

## Basic operating cycle

### 1. Import

Open **Import** and upload a supported file.

### 2. Preview

WorkHound parses the source into candidates but does **not** immediately create Work Items.

Review:

- candidate title;
- normalized fields;
- source context;
- possible duplicate indication.

### 3. Select

Choose the candidates that should be accepted.

### 4. Commit

Commit the selected candidates. WorkHound creates the Work Items and records the import batch.

### 5. Execute

Open a Work Item and maintain its:

- owner;
- status;
- priority;
- progress;
- ticket;
- other Work Item details.

Use **Save Work Item Details** for those fields.

### 6. Record evidence and progress

Use **Add Work Note** to append progress, evidence, decisions, blockers, follow-ups, or management context.

Use **Save Note Artifact**. This is intentionally separate from saving the Work Item itself.

### 7. Measure

Use Dashboard and Analytics to review execution state.

### 8. Report

Use Reports to download the management Markdown report.

---

# Import Minimum Standards

This section defines the **minimum data standards required by the v0.1.3 parser**, not an aspirational future schema.

## Universal requirements

Every import must meet these minimum conditions:

1. The file must be one of:
   - `.csv`
   - `.xlsx`
   - `.md`
   - `.markdown`
2. The upload must be no larger than **20 MB** under the default application configuration.
3. The file must contain enough recognizable structure for the appropriate adapter to produce at least one candidate.
4. Every candidate that becomes a Work Item must have a non-empty **title**.
5. The user must select the candidate in the import preview before it is committed.

If WorkHound cannot identify candidate work, the file may upload successfully while producing no usable candidates. This is different from a malformed or unsupported file.

---

# CSV and XLSX Import Contract

For CSV and XLSX, **the first row is the header row**.

The single mandatory semantic field is:

> **Title**

WorkHound must recognize one of the supported title aliases in the header row.

## Supported column aliases

Header matching is case-insensitive and surrounding whitespace is ignored.

| WorkHound field | Recognized source headers |
|---|---|
| **Title — REQUIRED** | `title`, `item`, `objective`, `task`, `work item`, `work_item` |
| Description | `description`, `details`, `detail` |
| Owner | `owner`, `assigned to`, `assignee` |
| Priority | `priority` |
| Status | `status`, `state` |
| Notes | `notes`, `comments` |
| Category | `category`, `initiative`, `group` |
| Progress % | `progress`, `progress percent`, `percent complete`, `% complete` |

You do **not** have to use WorkHound's preferred column names if one of the aliases above is present.

For example, all of these can identify the required title field:

```text
Title
Task
Objective
Work Item
work_item
```

## Recommended CSV/XLSX standard

For the best operational result, use:

```text
Title
Description
Category
Owner
Priority
Status
Progress
```

Example:

| Title | Description | Category | Owner | Priority | Status | Progress |
|---|---|---|---|---|---|---:|
| Reduce Long-Term Active Alerts | Review aging SolarWinds alerts and eliminate chronic noise | Alert Hygiene | Barney Gaumer | High | In Progress | 25 |
| Review Backbone Maps | Validate backbone and ISP documentation | Documentation | Network Team | Medium | Planned | 0 |

### CSV example

```csv
Title,Description,Category,Owner,Priority,Status,Progress
Reduce Long-Term Active Alerts,Review aging SolarWinds alerts and eliminate chronic noise,Alert Hygiene,Barney Gaumer,High,In Progress,25
Review Backbone Maps,Validate backbone and ISP documentation,Documentation,Network Team,Medium,Planned,0
```

## Title behavior

Rows with a blank title are skipped.

If no supported title header is found, the current CSV/XLSX adapter cannot create candidates from that file.

**Fix:** rename or add a header using one of the supported Title aliases.

## Description and Notes behavior

WorkHound prefers the mapped Description field.

If Description is absent or empty, the CSV/XLSX adapters can use the mapped Notes/Comments value as the candidate description.

The imported Notes column does **not** automatically become a timestamped Work Note Artifact in v0.1.3. It is source data used as candidate description fallback.

## Progress behavior

Progress may be supplied as a number or a string containing `%`.

Examples:

```text
25
25%
50.0
```

WorkHound converts the value to an integer and clamps it to:

```text
0 .. 100
```

A value that cannot be parsed becomes `0`.

## Priority and Status behavior

If the source omits these fields:

```text
Priority -> Medium
Status   -> New
```

v0.1.3 does not perform broad vocabulary translation for arbitrary priority/status terminology during CSV/XLSX parsing. For clean analytics, prefer the native values used by the Work Item editor.

Recommended priority values:

```text
Low
Medium
High
Critical
```

Recommended status values:

```text
New
Planned
In Progress
Blocked
Waiting
Completed
Deferred
Cancelled
```

## XLSX-specific behavior

v0.1.3:

- reads `.xlsx`;
- uses the workbook's **active worksheet**;
- treats its first row as headers;
- reads calculated cell values with `data_only=True`.

Other worksheets are not independently imported in the current release.

If the work is on another worksheet, make that sheet active before saving the workbook or export the desired data to a dedicated XLSX/CSV.

## CSV-specific behavior

CSV is decoded as UTF-8 with BOM support (`utf-8-sig`).

For maximum portability, export CSV files as UTF-8.

---

# Markdown Import Contract

Markdown is intentionally different from CSV/XLSX.

There is no required column schema. Instead, WorkHound uses document structure and action-oriented headings to identify candidate work.

## What becomes a candidate

In v0.1.3, a Markdown heading becomes a candidate when either:

1. it is a level-three-or-deeper heading (`###` through `######`), **or**
2. its heading text begins with a recognized action verb.

Recognized action verbs are currently:

```text
validate
review
create
align
socialize
improve
run
develop
verify
recommend
reduce
build
update
test
import
identify
generate
increase
eliminate
prevent
```

Matching is case-insensitive.

Therefore this can become work even as an H2:

```markdown
## Review Backbone and ISP Maps
```

And this becomes work because it is an H3:

```markdown
### Documentation Cleanup
```

even though `Documentation` is not one of the action verbs.

## Markdown hierarchy

Heading hierarchy provides context.

Example:

```markdown
# NOC Improvement Program

## Alert Hygiene

### Reduce Long-Term Active Alerts

- Review active SolarWinds alerts.
- Eliminate aging alerts.
- Reduce alert noise.
- Prevent alerts from remaining active for extended periods.
```

WorkHound interprets:

```text
Title:       Reduce Long-Term Active Alerts
Category:    Alert Hygiene
Description: bullet content beneath the candidate heading
```

The heading path is also retained as source-section context.

## Candidate description

After a candidate heading is opened, subsequent bullet lines and ordinary text are collected into its description until the parser reaches another Markdown heading that changes the structure.

Example:

```markdown
### Verify DR Documentation

Review the current recovery documentation.
Confirm diagrams match the deployed environment.
```

The ordinary text becomes candidate description content.

## Markdown priority inference

v0.1.3 contains one limited Markdown priority inference:

If the current heading path contains:

```text
high priority
```

the candidate receives:

```text
High
```

Otherwise the Markdown adapter defaults to:

```text
Medium
```

## Markdown owner/status/progress

The v0.1.3 Markdown adapter does **not** generically infer arbitrary owner, status, or progress metadata from prose.

Those values can be set after import in the Work Item editor.

This distinction is important: WorkHound is deterministic. It does not pretend to understand arbitrary prose that the parser has not been coded to interpret.

## Recommended Markdown pattern

For predictable imports:

```markdown
# Program or Meeting Name

## Category / Initiative

### Action-Oriented Work Item Title

- What needs to be done
- Desired outcome
- Important context
- Acceptance criteria
```

This structure gives the parser a strong title/category/description relationship while remaining easy for humans to read and generate.

---

# Import Examples

## Minimal valid CSV

```csv
Title
Review Backbone Maps
```

## Better CSV

```csv
Title,Description,Category,Owner,Priority,Status,Progress
Review Backbone Maps,Validate ISP and backbone diagrams,Documentation,Network Engineering,High,In Progress,40
```

## Alias-based CSV

This is also valid because `Task`, `Assigned To`, `State`, and `% Complete` are recognized aliases:

```csv
Task,Assigned To,State,% Complete
Review Backbone Maps,Network Engineering,In Progress,40
```

## Minimal useful Markdown

```markdown
# Operations

## Documentation

### Review Backbone Maps

- Validate current diagrams.
- Identify stale circuit information.
```

## Action-heading Markdown

```markdown
# Operations Review

## Reduce Long-Term Active Alerts

- Review active alerts.
- Eliminate aging noise.
```

`Reduce Long-Term Active Alerts` can become a candidate because `reduce` is a recognized action verb.

---

# Import Preview and Duplicate Detection

WorkHound does not blindly commit parsed data.

After parsing, candidates are placed into an import preview.

The operator decides which candidates should be accepted.

## Duplicate detection

v0.1.3 compares normalized candidate titles against existing Work Item titles using Python `SequenceMatcher`.

Title normalization:

- converts to lowercase;
- removes non-alphanumeric separators;
- collapses the title into normalized words.

A similarity score of **0.90 or greater** is treated as a possible duplicate.

Example:

```text
Review Backbone & ISP Maps
Review Backbone and ISP Maps
```

may be similar enough to generate a warning.

### Important

Duplicate detection is a **warning mechanism**, not a hard uniqueness constraint.

A selected candidate can still be committed even when a possible duplicate exists. This is intentional because repeated or similarly named work can be legitimate.

The operator remains the approval authority.

---

# Canonical Work Item Model

The internal `WorkItem` model contains more fields than every current adapter populates.

Key fields include:

```text
title
description
category
work_type
priority
status
owner
stakeholder
source
source_batch_id
source_section
source_text
created_date
target_date
completed_date
progress_percent
disposition
notes
ticket
external_reference
parent_id
```

This is deliberate.

The source document is not allowed to redefine the database every time a spreadsheet changes.

## Work types available in the editor

```text
TASK
PROJECT
VALIDATION
INVESTIGATION
IMPROVEMENT
LEARNING
DOCUMENTATION
OPERATIONAL
FOLLOW_UP
RECOMMENDATION
```

## Priorities

```text
Low
Medium
High
Critical
```

## Statuses

```text
New
Planned
In Progress
Blocked
Waiting
Completed
Deferred
Cancelled
```

## Progress

Progress is stored as an integer percentage from `0` through `100`.

When a Work Item is saved with status `Completed`, WorkHound records a completed date if one is not already present.

---

# Work Note Artifacts

Operational notes are modeled as append-only **Work Note Artifacts** rather than one continuously overwritten text box.

Each artifact contains:

- artifact ID;
- Work Item association;
- owner;
- note body;
- creation timestamp.

Timestamps are stored/displayed as UTC in the v0.1.3 workflow.

## Why artifacts instead of one Notes field?

A mutable Notes field answers:

> What does the note say now?

Artifacts answer:

> What did we know, decide, accomplish, or encounter over time — and who recorded it?

Example:

```text
Work Item: Reduce Long-Term Active Alerts

Artifact #1
Owner: Barney Gaumer
Timestamp: 2026-08-12 20:11:35 UTC
Built and tested alert-analysis tooling...

Artifact #2
Owner: Network Team
Timestamp: 2026-08-19 14:05:02 UTC
Reviewed chronic alert candidates...

Artifact #3
Owner: Barney Gaumer
Timestamp: 2026-08-26 18:42:11 UTC
Validated reduction in long-term active alerts...
```

## Owner behavior

The artifact owner defaults to the Work Item owner.

It can be overridden for an individual artifact without changing the Work Item's primary owner.

## Separate save operations

WorkHound deliberately separates:

**Save Work Item Details**

from:

**Save Note Artifact**

This prevents adding a note from accidentally resubmitting or changing the rest of the Work Item.

After a note is saved, WorkHound redirects back to the Work Item. The note-entry field is empty and ready for the next artifact.

## Legacy Notes

Work Items created under earlier versions may contain the original mutable `notes` field.

v0.1.3 preserves and displays this content as **Legacy Note** rather than discarding it.

---

# Dashboard and Analytics

## Dashboard

The Dashboard provides an immediate operational snapshot, including:

- total Work Items;
- In Progress count;
- Blocked count;
- Completed count;
- completion rate;
- work by status;
- work by priority;
- recent work.

## Analytics

The Analytics view provides a management-oriented execution picture.

Current metrics include:

- operational health score;
- active work;
- average active progress;
- completion rate;
- blocked count;
- waiting count;
- High/Critical open count;
- active work older than 30 days;
- active work older than 60 days;
- initiative/category performance;
- status distribution;
- blocked-work drill-down;
- high-priority open-work drill-down.

## Operational health score

The score is **not AI-generated**.

It is a deterministic local heuristic using:

- completion rate;
- average active progress;
- blocker penalty;
- aging-work penalty.

It is intended as a compact management signal, not as a formal SLA, risk score, or predictive model.

Organizations should interpret it in the context of their own work-management practices.

---

# Management Reporting

The Reports area can generate a Markdown management report.

The report includes an executive snapshot such as:

- total tracked work;
- active work;
- In Progress work;
- Blocked work;
- Completed work;
- completion rate;
- average active progress;
- High/Critical open work;
- aging work;
- operational health.

It also includes initiative/category rollups and status-oriented Work Item sections.

When a Work Item has Work Note Artifacts, the report can include its latest artifact context.

The generated report is Markdown so it remains:

- portable;
- human-readable;
- version-control friendly;
- easy to paste into other reporting systems;
- easy to use as downstream context.

---

# Import Batches and Provenance

Every committed import creates an `ImportBatch`.

Batch information includes:

```text
filename
source type
import timestamp
detected candidates
accepted candidates
rejected candidates
possible duplicate count
raw source text where available
```

Each imported Work Item can retain:

```text
source filename
source batch ID
source section
source text
```

This creates a provenance chain:

```text
Original File
    |
Import Batch
    |
Candidate
    |
Committed Work Item
    |
Source Evidence
```

That provenance is a major design goal. WorkHound should not merely tell you that a task exists; it should retain useful evidence about where that task came from.

### Raw source storage note

For CSV and Markdown imports, v0.1.3 stores up to the first **500,000 characters** of document raw text in the preview/session data that is subsequently associated with the import batch.

XLSX candidates retain row-level source evidence, but the XLSX adapter does not currently produce a full workbook `raw_text` representation.

---

# Setup and Administration

The Setup page provides:

- application name;
- default owner;
- report organization/team;
- update channel;
- installed version;
- instance path;
- system information;
- release-ZIP update interface;
- recent update backups;
- staged-update status.

Application settings are stored in the local database.

---

# Updating WorkHound

v0.1.3 includes an in-application **Update from Release ZIP** workflow.

## Update workflow

From **Setup**:

1. Choose a complete WorkHound release ZIP.
2. Select **Validate & Stage Update**.
3. WorkHound verifies that the upload is a valid ZIP.
4. ZIP member paths are checked to prevent path traversal.
5. WorkHound verifies that the archive contains exactly one recognizable application root with:
   - `run.py`
   - `workhound/version.py`
6. The release version is read from `workhound/version.py`.
7. The release must use supported numeric WolfPack versioning.
8. The release must be newer than the running release.
9. A timestamped pre-update backup is created.
10. The uploaded release is retained in update staging.
11. Application files are overlaid.
12. `instance/` and `.venv/` are preserved.
13. WorkHound writes an update marker.
14. Restart the WorkHound process normally.

## Important update behavior

The updater does **not** attempt to kill or hot-reload its own Python process.

After staging:

```bash
# stop the currently running process using your normal process-control method

cd /path/to/workhound
source .venv/bin/activate
python run.py --version
python run.py --host 0.0.0.0 --port 5000
```

## Supported version form

Examples:

```text
0.1.3
0.1.3-hf1
0.1.4
```

The in-app updater requires the uploaded release to compare newer than the currently running version.

## Update backups

In-app backups are stored under:

```text
instance/update_backups/
```

Uploaded/staged release archives are stored under:

```text
instance/update_staging/
```

Do not remove known-good backups until the new release has been validated.

---

# Data Storage and Backup

The default SQLite database is:

```text
instance/workhound.db
```

This database contains operational state and should be treated as persistent data.

## Back it up

At minimum, back up:

```text
instance/workhound.db
```

For a more complete application-state backup, preserve the entire:

```text
instance/
```

directory.

## Do not commit runtime data

The included `.gitignore` excludes the common local database files under `instance/`.

Before publishing a fork or contribution, verify that your repository does not contain:

- operational databases;
- imported source data;
- internal reports;
- credentials;
- private artifacts;
- environment-specific secrets.

---

# Security and Deployment Notes

WorkHound v0.1.3 is an early operational release.

## Flask secret key

The current application source contains a development/default Flask `SECRET_KEY`.

**Change this before using WorkHound in an untrusted or production environment.**

Because Flask sessions are signed using this value, a public deployment should use a strong environment-specific secret rather than the repository default.

## Built-in Flask server

`python run.py` launches Flask's built-in server.

That is convenient for local use and trusted lab/engineering environments, but the Flask development server should not be treated as a hardened Internet-facing production deployment.

For broader deployment, place WorkHound behind an appropriate production WSGI/service architecture and apply your organization's:

- authentication;
- authorization;
- TLS;
- reverse-proxy;
- host firewall;
- logging;
- backup;
- monitoring;
- service-management controls.

## Authentication

v0.1.3 does not implement a complete application authentication/RBAC layer.

Do not expose an unauthenticated WorkHound instance containing operational data to untrusted networks.

## Imported data

Treat uploaded documents as operational data.

Source evidence and note artifacts may contain:

- internal hostnames;
- project information;
- owner names;
- tickets;
- incident context;
- other organization-specific information.

Protect the database and host accordingly.

## Release updater

The in-app updater modifies application code.

Only trusted administrators should have access to Setup and only trusted WorkHound release ZIPs should be uploaded.

The updater validates archive structure and protects against ZIP path traversal, but v0.1.3 does **not** implement cryptographic release signing.

---

# Troubleshooting Imports

## "Unsupported file type"

Supported extensions are:

```text
.csv
.xlsx
.md
.markdown
```

Convert other formats before importing.

## CSV/XLSX uploads but produces no candidates

Check the first row.

You need at least one recognized Title alias:

```text
title
item
objective
task
work item
work_item
```

Example fix:

```text
Problem Name
```

becomes:

```text
Title
```

## XLSX imports the wrong data

v0.1.3 reads the workbook's active worksheet.

Activate the desired sheet and save the workbook, or export that sheet to CSV/XLSX separately.

## Progress becomes zero

Use a numeric value or a percentage-like value:

```text
25
25%
25.0
```

Non-numeric text becomes `0`.

## Markdown produces too many candidates

Remember that every H3-H6 heading can become a candidate.

Use H1/H2 for document organization and reserve H3+ for actual work items when possible.

## Markdown misses an H1/H2 action item

For H1/H2 headings, begin the title with a currently recognized action verb.

Instead of:

```markdown
## Backbone Maps
```

use:

```markdown
## Review Backbone Maps
```

Or structure it as an H3:

```markdown
### Backbone Maps
```

## Duplicate warning appears

The title is at least approximately 90% similar to an existing Work Item after normalization.

Review it. The warning does not automatically block import.

## File is rejected for size

The default maximum request size is 20 MB.

Large exports should be reduced, split, or preprocessed before import unless you intentionally change the application configuration.

---

# Known Limitations

v0.1.3 intentionally has a focused scope.

Current limitations include:

- CSV/XLSX field aliases are a defined list, not arbitrary semantic inference.
- XLSX imports only the active worksheet.
- Legacy `.xls` is not supported.
- Markdown extraction is rule-based rather than LLM-based.
- Markdown owner/status/progress are not generically inferred from prose.
- Duplicate detection is title-similarity based and can produce false positives or miss semantic duplicates with dissimilar titles.
- Duplicate warnings do not prevent an operator from importing the candidate.
- Imported source priority/status strings are not comprehensively normalized to every possible external vocabulary.
- No full authentication/RBAC layer is included in v0.1.3.
- The default launch path uses Flask's built-in server.
- The in-app updater does not cryptographically sign/verify releases.
- The updater stages/overlays code but requires an external process restart.
- SQLite is the default persistence layer.
- Schema evolution currently relies on SQLAlchemy `create_all()` for additive tables; a full migration framework is not yet included.

These are useful contribution areas, but changes should preserve the canonical-model and provenance principles.

---

# Project Structure

```text
workhound-v0.1.3/
├── run.py
├── requirements.txt
├── README.md
├── CHANGELOG.md
├── docs/
│   └── WorkHound_Architecture_and_Product_Plan_v0.1.0.md
└── workhound/
    ├── __init__.py
    ├── analytics.py
    ├── import_engine.py
    ├── models.py
    ├── normalizer.py
    ├── reports.py
    ├── routes.py
    ├── updater.py
    ├── version.py
    ├── adapters/
    │   ├── base.py
    │   ├── csv_adapter.py
    │   ├── markdown_adapter.py
    │   └── xlsx_adapter.py
    ├── static/
    └── templates/
```

## Major components

### `adapters/`

Source-specific parsing.

Adapters translate external representations into `WorkCandidate` objects.

### `import_engine.py`

Selects the appropriate adapter by file extension.

### `normalizer.py`

Contains title normalization and possible-duplicate detection.

### `models.py`

Defines persistent canonical models:

- `ImportBatch`
- `WorkItem`
- `WorkHistory`
- `AppSetting`
- `WorkNote`

### `analytics.py`

Calculates dashboard/management analytics.

### `reports.py`

Builds management Markdown reporting.

### `updater.py`

Validates and stages complete WorkHound release ZIPs and maintains pre-update backups.

---

# Versioning

WorkHound uses numeric release versions.

Examples:

```text
v0.1.3
v0.1.3-hf1
v0.1.4
```

Hotfix suffixes are numeric.

Release ZIPs intended for the in-app updater must contain a version in `workhound/version.py` that is newer than the running release.

---

# Contributing

Contributions are welcome.

When modifying WorkHound, preserve these principles:

1. **The canonical model owns the schema.**  
   Do not let one source format redefine the core database model.

2. **Adapters isolate source-specific logic.**  
   New import formats should normally be implemented as adapters.

3. **Preview before commit.**  
   Parsing source data should not silently create operational work.

4. **Preserve provenance.**  
   Imported Work Items should retain useful evidence about their source.

5. **Human approval remains authoritative.**  
   Duplicate detection and parser confidence are decision support, not unquestionable truth.

6. **Do not overwrite operational history when an artifact is more appropriate.**  
   Work Note Artifacts exist to preserve a timeline.

7. **Keep analytics explainable.**  
   If a score is deterministic, document how it is derived. Do not label heuristics as AI.

8. **Protect persistent state during upgrades.**  
   `instance/` and the database are operational data, not disposable application code.

9. **Keep release versions numeric and predictable.**

Before submitting changes:

```bash
python -m py_compile run.py workhound/*.py workhound/adapters/*.py
python run.py --version
```

Test at minimum:

- CSV import;
- XLSX import;
- Markdown import;
- preview/commit;
- duplicate warning;
- Work Item editing;
- independent note-artifact save;
- Dashboard;
- Analytics;
- management report;
- Setup;
- release-update validation when updater code is changed.

---

## Philosophy

WorkHound is not intended to be another place where operational data goes to die.

The objective is to turn scattered evidence into a managed execution trail:

```text
INGEST
  -> NORMALIZE
    -> REVIEW
      -> COMMIT
        -> EXECUTE
          -> DOCUMENT
            -> MEASURE
              -> REPORT
```

**Raw information in. Accountable work out.**
