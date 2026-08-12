# Changelog

## v0.1.3 — 2026-08-12

- Split Work Item Details and Work Note Artifact saves into independent forms/actions
- Added dedicated **Save Work Item Details** button
- Added dedicated **Save Note Artifact** button
- Note save no longer resubmits or rewrites Work Item detail fields
- Preserved timestamped note artifact behavior and owner override
- Added AlertHound-style **Update from Release ZIP** administration workflow
- Release updater validates WorkHound package structure and numeric WolfPack version
- Rejects same/older release versions
- Protects against ZIP path traversal
- Creates timestamped pre-update ZIP backups under `instance/update_backups`
- Preserves `instance/` and `.venv/`
- Stages uploaded release ZIP under `instance/update_staging`
- Overlays application code and records restart-required marker
- Setup page displays recent update backups and staged-update status


## v0.1.2 — 2026-08-12

- Converted ongoing work notes into append-only Work Note artifacts
- Every artifact receives a database ID and creation timestamp
- Artifact timestamps are displayed to second resolution in UTC
- Artifact owner defaults to the Work Item owner but supports per-artifact override
- Saving appends the artifact and clears the note-entry field via Post/Redirect/Get
- Existing v0.1.0/v0.1.1 notes remain visible as Legacy Notes
- Work History records artifact creation with owner and timestamp
- Management report includes the latest artifact ID, owner, timestamp, and note
- Added `work_note` table using safe schema initialization during upgrade


## v0.1.1 — 2026-08-12

- Added management-oriented Analytics tab
- Added local SVG status graph with no CDN dependency
- Added execution, blocker, priority, aging, progress, and completion statistics
- Added initiative/category performance rollups
- Added operational health heuristic
- Expanded management Markdown report with executive snapshot and initiative rollup
- Added persistent Setup settings
- Added future Update From ZIP framework/documentation
- Preserved local-first deterministic architecture


## v0.1.0 — 2026-08-12

Initial WorkHound release.

- Canonical work model
- CSV/XLSX/Markdown adapters
- Candidate normalization boundary
- Import preview and batch tracking
- Source provenance
- Duplicate candidate warning
- Work queue and editing
- Status/progress/history tracking
- Dashboard analytics
- Management Markdown report
- Setup/admin page
