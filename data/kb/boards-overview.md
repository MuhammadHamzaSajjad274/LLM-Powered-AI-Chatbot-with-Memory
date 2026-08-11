# Boards Overview

Boards are the central organizing unit in FlowBoard. Each board represents a project, product area, or team workflow and contains columns (lists), task cards, labels, and optional swimlanes. Understanding board structure helps you design workflows that match how your team actually works.

## Columns and WIP Limits

Columns represent stages in your process—common setups include Backlog → Ready → In Progress → Review → Done, though FlowBoard imposes no template requirements. Each column can have a **Work-in-Progress (WIP) limit**. When the limit is reached, the column header turns amber and new cards cannot enter until existing ones move forward. Admins set WIP limits under **Board Settings → Columns**.

## Board Types

FlowBoard supports three board types. **Kanban boards** use drag-and-drop columns with no fixed timeboxes. **Sprint boards** add iteration boundaries: you assign tasks to two-week (default) sprints and use the Sprint Planner view to commit work. **Roadmap boards** display tasks on a timeline by start/end dates rather than columns—ideal for quarterly planning.

## Card Anatomy

Every task card shows title, assignee avatar, due date badge, label chips, and attachment count. Click a card to open the detail panel with description (Markdown supported), checklist, comments thread, activity log, and linked pull requests if GitHub is connected. Cards can have **subtasks** that roll up completion percentage to the parent.

## Board Permissions

Board-level permissions override workspace defaults. A board can be **Private** (explicit members only), **Team** (all workspace members), or **Public link** (view-only URL without login). Sensitive HR or finance boards should always remain Private with Viewer-only access for auditors.

## Archiving and Templates

Completed boards can be archived—they remain searchable but hidden from the active board list. Save any board as a **Template** to clone its column structure, labels, and automation rules for new projects. Templates do not copy task content, only structure.
