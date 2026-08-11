# Tasks and Subtasks

Tasks (also called cards) are the atomic unit of work in FlowBoard. This document covers creation, fields, subtasks, dependencies, and bulk operations.

## Creating and Editing Tasks

Create tasks via **Add Task** in any column, the `N` keyboard shortcut, or by converting a comment into a task. Required field: **Title** (max 200 characters). Optional fields include **Description** (Markdown, 50,000 character limit), **Assignee**, **Due date**, **Priority** (Low/Medium/High/Urgent), **Labels**, and **Estimated hours**.

Due dates trigger notifications at 9:00 AM workspace local time on the due date and again if overdue by 24 hours. Overdue cards display a red border on the board.

## Subtasks and Checklists

**Subtasks** are independent child tasks linked to a parent—they appear on the board if assigned a column, or only in the parent detail panel if unassigned. Completing all subtasks does not auto-close the parent unless the **Auto-complete parent** automation is enabled.

**Checklists** are lightweight inline items within a single task—ideal for acceptance criteria. Checklist progress appears as a fraction on the card face (e.g., 2/5).

## Task Dependencies

Link tasks with **Blocks** or **Blocked by** relationships. A blocked task shows a grey overlay and cannot move to Done until blockers resolve. FlowBoard displays dependency arrows in the **Timeline view**. Circular dependencies are rejected with error code `FB-409`.

## Bulk Actions

Select multiple cards with `Shift+Click` or `Cmd/Ctrl+Click`, then use the bulk toolbar to reassign, relabel, move columns, or set due dates. Bulk delete requires Admin role and sends a confirmation email to the board owner.

## Task Search and Filters

Global search (`/`) indexes titles, descriptions, and comments. Board filters support assignee, label, priority, due date range, and custom field queries. Save filter combinations as **Views** for one-click access.
