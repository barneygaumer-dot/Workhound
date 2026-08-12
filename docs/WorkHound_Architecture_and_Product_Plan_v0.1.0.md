# WorkHound --- Operational Work Intelligence

## Product Concept and Initial Architecture Plan

**Project:** WolfPack WorkHound\
**Initial Release Target:** v0.1.0\
**Purpose:** Ingest semi-structured and structured work data, normalize
it into a consistent operational work model, organize execution, track
progress, and provide dashboards, analytics, reporting, and source
traceability.

------------------------------------------------------------------------

## 1. Mission

WorkHound is a WolfPack application for turning work-related data from
multiple sources into an actionable operational work intelligence
system.

The initial supported inputs are:

-   CSV
-   XLSX
-   Markdown

The application should accept both structured exports and
semi-structured AI/meeting summaries, identify actionable work,
normalize it into a stable internal model, allow the user to manage
execution, and produce useful analytics and management reporting.

The core question WorkHound answers is:

> **What work exists, who owns it, what is moving, what is stuck, and
> what are we actually accomplishing?**

WorkHound should use the same general architectural philosophy as
AlertHound: adapter-driven imports, a normalized internal data model,
import-batch tracking, dashboards, reporting, setup/admin capabilities,
and a framework that can be extended without redesigning the application
every time an upstream data source changes.

------------------------------------------------------------------------

## 2. Design Principle

The most important architectural rule is:

> **Imports do not define WorkHound's database schema. The WorkHound
> schema defines what imported information becomes.**

CSV columns, spreadsheet layouts, Markdown structure, Copilot output,
and future data sources are external representations.

WorkHound owns the canonical internal representation.

This separation allows upstream formats to change without forcing
changes throughout the application.

------------------------------------------------------------------------

## 3. High-Level Architecture

``` text
            CSV
             |
            XLSX
             |
             MD
             |
             v
     +-------------------+
     |  IMPORT ADAPTERS  |
     |                   |
     | csv_adapter       |
     | xlsx_adapter      |
     | markdown_adapter  |
     | future adapters   |
     +---------+---------+
               |
               v
     +-------------------+
     | NORMALIZATION     |
     | ENGINE            |
     |                   |
     | identify records  |
     | classify work     |
     | extract metadata  |
     | preserve source   |
     +---------+---------+
               |
               v
       WORKHOUND DATA MODEL
               |
      +--------+--------+
      |        |        |
      v        v        v
    DASH     WORK     REPORTS
             QUEUE
```

The import pipeline should be:

``` text
Raw File
   |
   v
Format Adapter
   |
   v
Document Model
   |
   v
Candidate Work Items
   |
   v
Normalizer
   |
   v
Validation
   |
   v
Preview
   |
   v
Commit
```

**Parsers should never write directly into production work tables.**

The intermediary representation creates a controlled boundary between
unpredictable source data and the WorkHound data model.

------------------------------------------------------------------------

## 4. Core Work Model

The central WorkHound object should be a **Work Item**, rather than
merely a task.

A task might be:

> Create ISP playbook.

A work item may represent:

-   Create ISP playbook
-   Validate chronic alert reporting
-   Improve SolarWinds proficiency
-   Review backbone maps
-   Reduce stale alerts
-   Socialize playbooks
-   Learn Power BI
-   Validate documentation
-   Investigate an operational issue
-   Implement an improvement

This permits WorkHound to represent operational work, development,
learning, validation, investigations, projects, recommendations, and
follow-up activity using one consistent framework.

### Initial `work_item` model

``` text
work_item
---------
id
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

Supporting tables should hold information that naturally grows over
time:

``` text
work_item_history
work_item_comment
work_item_tag
work_item_metric
work_item_relationship
import_batch
import_record
source_document
```

This avoids turning the primary table into an oversized catch-all
schema.

------------------------------------------------------------------------

## 5. Work Types

Initial work classifications:

``` text
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

Additional types can be added later without changing the basic
architecture.

WorkHound should also eventually distinguish higher-level management
information such as:

``` text
OBJECTIVE
EXPECTATION
WORK_ITEM
MILESTONE
ACCOMPLISHMENT
```

This allows the application to track not only individual tasks, but also
professional objectives and management expectations against actual work
performed.

------------------------------------------------------------------------

## 6. Status and Progress

Status and progress should remain separate.

### Initial status model

``` text
New
Planned
In Progress
Blocked
Waiting
Completed
Deferred
Cancelled
```

A separate `progress_percent` field provides completion measurement.

Example:

``` text
Status: In Progress
Progress: 80%
```

or:

``` text
Status: Blocked
Progress: 25%
```

This distinction improves dashboard and management reporting accuracy.

------------------------------------------------------------------------

## 7. Parent / Child Work

WorkHound should support hierarchical work.

For example:

``` text
Validate Chronic Alert Reporting Tool
|
+-- Test against real SolarWinds data
+-- Import additional exports
+-- Test all SolarWinds instances
+-- Validate against known chronic issues
```

Child work can optionally roll progress into the parent.

For example, if three of four equally weighted child items are complete:

``` text
Parent progress = 75%
```

Later releases may support weighted children.

------------------------------------------------------------------------

## 8. Import Engine

The import engine is a major architectural component.

Each adapter converts its source format into a common intermediary
representation.

Example conceptual document:

``` python
ImportedDocument(
    source_type="markdown",
    title="1:1 Meeting Summary",
    metadata={...},
    sections=[...],
    candidate_items=[...]
)
```

Candidate work should be represented independently from committed
database records:

``` python
WorkCandidate(
    title="Review Playbooks Against Real Incidents",
    category="High Priority",
    description="Compare existing playbooks...",
    source_path=[
        "Action Items",
        "High Priority"
    ],
    confidence=0.96
)
```

This enables validation and preview before anything becomes active work.

------------------------------------------------------------------------

## 9. Import Preview

All imports---especially Markdown and other semi-structured
sources---should support preview before commit.

Example:

``` text
IMPORT PREVIEW
--------------------------------------------

12 Work Items Detected
27 Supporting Actions Detected

[x] Validate Chronic Alert Reporting Tool
[x] Review Playbooks Against Real Incidents
[x] Create ISP / Internet Outage Playbook
[x] Align Playbooks With SolarWinds Alert Instructions
[x] Socialize Playbooks With NOC Team
...

[ Import Selected ]
```

The user should be able to:

-   Accept candidates
-   Reject candidates
-   Edit candidates
-   Merge potential duplicates
-   Change classification
-   Change parent/child relationships
-   Commit only selected items

------------------------------------------------------------------------

## 10. CSV / XLSX Mapping Engine

Structured imports should use configurable field mapping.

Example source:

``` text
Objective
Owner
Priority
Target
Status
Notes
```

Mapping:

``` text
Objective -> title
Owner     -> owner
Priority  -> priority
Target    -> target_date
Status    -> status
Notes     -> notes
```

A different source may contain:

``` text
Item
Assigned To
Due
State
Comments
```

which can map to the same canonical schema:

``` text
Item        -> title
Assigned To -> owner
Due         -> target_date
State       -> status
Comments    -> notes
```

Mapping profiles should be reusable.

Examples:

``` text
Mehrdad-Q3-Objectives
Copilot-1on1
NOC-Projects
PowerBI-Export
```

This makes repeat imports fast while keeping WorkHound independent of
source column names.

------------------------------------------------------------------------

## 11. Markdown Adapter

The Markdown adapter should interpret document hierarchy and language
patterns.

Initial structural recognition:

``` text
# / ## headings
    -> section/category

### numbered heading
    -> candidate work item

- bullet
    -> detail/subtask/criterion

Goal:
    -> goal metadata

Missing:
    -> gap/action
```

Strong action verbs can increase confidence that a heading represents
actionable work:

``` text
Validate
Review
Create
Improve
Develop
Reduce
Recommend
Verify
Align
Socialize
```

Markdown parsing should be deterministic in the initial release.

AI should **not** be required for the core import process.

An optional AI-assisted adapter or enrichment layer can be introduced
later for poorly structured documents.

------------------------------------------------------------------------

## 12. Source Traceability

Every imported work item should retain provenance.

Example:

``` text
Source:
Barney_Mehrdad_1on1_Summary_2026-08-12.md

Import batch:
2026-08-12-001

Source section:
Action Items -> High Priority

Original text:
...
```

The UI should provide a **Show Source** function so users can inspect
the original evidence behind an imported item.

This is consistent with the WolfPack Evidence Engineering philosophy.

------------------------------------------------------------------------

## 13. Import Batch Management

Each ingestion operation should create an import batch.

Example:

``` text
Import #17
--------------------------------
Filename: Barney_Mehrdad_1on1_Summary_2026-08-12.md
Format: Markdown
Imported: Aug 12 2026
Detected: 12
Accepted: 12
Rejected: 0
Duplicates: 0
```

Batch actions should eventually include:

``` text
View
Reprocess
Delete Batch
```

Deletion must be designed carefully.

A work item originating from an import may later acquire:

-   Manual edits
-   Status history
-   Comments
-   Ticket references
-   Additional source references
-   Relationships
-   Progress updates

Deleting an old import should therefore not blindly destroy useful
operational history.

Provenance-aware deletion or reference-count behavior should be
considered.

------------------------------------------------------------------------

## 14. Duplicate Detection

Repeated meeting notes and exports will create duplicate candidates.

Initial duplicate detection can use a fingerprint derived from:

``` text
normalized_title
+ category
+ source context
```

The preview interface should identify likely duplicates.

Example:

``` text
Possible Duplicate

Existing:
Review Backbone and ISP Maps

Incoming:
Review backbone / ISP maps

Similarity: 94%

[ Merge ]
[ Import New ]
[ Ignore ]
```

Later versions can improve matching using additional metadata and
similarity scoring.

------------------------------------------------------------------------

## 15. Work History

Every meaningful change should be logged.

Example:

``` text
08/12 Created from Copilot import
08/13 Assigned to Barney
08/14 Status -> In Progress
08/20 Progress -> 50%
08/27 Added note
09/02 Status -> Completed
```

History turns WorkHound from a simple task tracker into a work evidence
system.

------------------------------------------------------------------------

## 16. Dashboard

The dashboard should provide immediate operational visibility.

### Summary cards

``` text
+------------+ +------------+ +------------+ +------------+
| OPEN       | | IN PROGRESS| | BLOCKED    | | COMPLETED  |
|    17      | |     8      | |     2      | |     24     |
+------------+ +------------+ +------------+ +------------+
```

### Initial dashboard analytics

-   Work by Status
-   Work by Category
-   Work by Priority
-   Completion Trend
-   Aging Work
-   Recently Completed
-   Upcoming Due Dates
-   Blocked Work
-   Top Active Initiatives

### Initiative progress

``` text
Alert Analytics              ########-- 80%
NOC Playbooks                ######---- 60%
SolarWinds Proficiency       #####----- 50%
Infrastructure Visibility    ###------- 30%
Power BI                     ##-------- 20%
```

The dashboard should support drill-down from metrics into the underlying
work.

------------------------------------------------------------------------

## 17. Reporting

WorkHound should support saved operational and management reports.

Initial report concepts:

``` text
Executive Status Report
Completed This Month
Open High-Priority Work
Blocked Items
Work Aging >30 Days
Work by Owner
Work by Initiative
Work by Source
Management 1:1 Report
```

### Management Progress Report

Example:

``` text
Period: August 2026

Completed
---------
4 items

In Progress
-----------
7 items

Blocked
-------
1 item

Major Accomplishments
---------------------
...

Operational Improvements
------------------------
...

Next Actions
------------
...
```

Initial export targets:

``` text
HTML
CSV
XLSX
Markdown
```

PDF can be added later if needed.

------------------------------------------------------------------------

## 18. Management / 1:1 Intake Mode

A high-value future capability is a dedicated intake mode for meeting
summaries and AI-generated notes.

A user should be able to import a summary and receive an analysis such
as:

``` text
NEW WORK DETECTED
-----------------
12 Action Items

NEW EXPECTATIONS
----------------
5

ACCOMPLISHMENTS
---------------
3

FOLLOW-UPS
----------
4

POTENTIAL METRICS
-----------------
6
```

This mode should recognize that meeting summaries contain more than
tasks.

They may contain:

-   New action items
-   Existing accomplishments
-   Management expectations
-   Objectives
-   Follow-ups
-   Gaps
-   Metrics
-   Recommendations
-   Learning objectives

This creates a path toward automatically correlating management
expectations with completed operational work and simplifying periodic
and annual performance reporting.

------------------------------------------------------------------------

## 19. Initial Technology Stack

WorkHound should initially remain simple, local-first, and consistent
with the WolfPack application family.

Proposed stack:

``` text
Python
Flask
SQLAlchemy
SQLite
Bootstrap
Chart.js
openpyxl
Python csv support
Markdown parser
```

AI services should not be required for the MVP.

The deterministic core should remain fully functional without external
AI dependencies.

------------------------------------------------------------------------

## 20. Initial Application Layout

Proposed routes:

``` text
/dashboard
/work
/work/<id>
/imports
/import
/reports
/admin
/setup
```

Proposed adapter structure:

``` text
adapters/
    base.py
    csv_adapter.py
    xlsx_adapter.py
    markdown_adapter.py
```

Proposed core modules:

``` text
import_engine.py
normalizer.py
models.py
analytics.py
reports.py
```

A more complete package layout can be defined when implementation
begins.

------------------------------------------------------------------------

## 21. MVP Scope --- v0.1.0

The v0.1.0 objective should be a usable vertical slice rather than a
large feature dump.

### Core

-   Flask application framework
-   SQLite database
-   SQLAlchemy models
-   Work item CRUD
-   Parent/child work relationships
-   Status tracking
-   Progress tracking
-   Priority
-   Category
-   Owner
-   Notes
-   Work history

### Imports

-   CSV import
-   XLSX import
-   Markdown import
-   Canonical intermediary import model
-   Import preview
-   Import batches
-   Source provenance
-   Basic duplicate detection
-   Reusable CSV/XLSX mapping

### Dashboard

-   Open work
-   In-progress work
-   Blocked work
-   Completed work
-   Status analytics
-   Priority analytics
-   Aging work
-   Initiative/category progress
-   Drill-down

### Reporting

-   Executive status
-   Completed work
-   Open high-priority work
-   Blocked work
-   Aging work
-   Management progress report
-   Markdown/CSV/XLSX/HTML export where practical

### Administration

-   Setup/admin page
-   Import batch management
-   Basic application configuration
-   Version display

------------------------------------------------------------------------

## 22. Deferred Capabilities

Potential post-v0.1.0 capabilities include:

-   AI-assisted unstructured document extraction
-   MCP interface
-   Advanced similarity/duplicate detection
-   Weighted parent/child progress
-   Automated recurring reports
-   Ticketing-system integration
-   SolarWinds integration
-   Power BI integration
-   Additional import adapters
-   User authentication / multi-user operation if required
-   Workflow automation
-   Notifications
-   PDF reporting
-   Objective-to-accomplishment correlation
-   Annual-review reporting
-   Trend and throughput analytics
-   Workload forecasting

------------------------------------------------------------------------

## 23. Product Position Within WolfPack

WorkHound complements AlertHound rather than replacing it.

**AlertHound answers:**

> What is the environment doing?

**WorkHound answers:**

> What are we doing about it?

Together they create a natural operational loop:

``` text
OBSERVE
   |
   v
AlertHound
   |
   v
IDENTIFY / ANALYZE
   |
   v
WorkHound
   |
   v
ASSIGN / EXECUTE
   |
   v
TRACK / REPORT
   |
   v
IMPROVE
   |
   +---------------------> OBSERVE
```

Future WolfPack integration could allow an AlertHound finding to
generate or link directly to WorkHound work while retaining evidence and
provenance across both applications.

------------------------------------------------------------------------

## 24. Product Philosophy

WorkHound should remain:

-   Local-first
-   Deterministic at its core
-   Evidence-driven
-   Source-traceable
-   Import-format agnostic
-   Easy to operate
-   Easy to upgrade
-   Extensible through adapters
-   Useful to engineers
-   Useful to management without becoming management bureaucracy

The system should reduce manual reporting rather than create another
system that requires constant administrative maintenance.

------------------------------------------------------------------------

## 25. Initial Success Criteria

WorkHound v0.1.0 succeeds if the user can:

1.  Launch the application.
2.  Import CSV, XLSX, or Markdown.
3.  Preview detected work before committing it.
4.  Normalize different source formats into the same work model.
5.  Organize work by category, priority, owner, and status.
6.  Track progress and history.
7.  Trace every imported item back to its source.
8.  Detect likely duplicate work.
9.  View useful operational analytics on a dashboard.
10. Produce a credible management progress report without manually
    reconstructing the work history.

------------------------------------------------------------------------

## 26. Guiding Statement

The initial sample meeting summary captured the operating direction
well:

> **Build less. Operate more. Analyze more. Drive improvements from
> data.**

WorkHound exists to make that measurable.

------------------------------------------------------------------------

# WolfPack Bottom Line

**WorkHound --- Operational Work Intelligence**

AlertHound tells us what the environment is doing.

**WorkHound tells us what we're doing about it.**

The architecture should preserve the WolfPack pattern: ingest
heterogeneous evidence, normalize it into a stable internal
representation, maintain provenance, turn the resulting data into
actionable intelligence, and provide a clean operational interface for
execution and reporting.
