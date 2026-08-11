# Notifications and Views

FlowBoard helps teams stay informed without overload through configurable notifications, saved views, and dashboard widgets.

## Notification Channels

Three channels exist: **in-app** (bell icon feed), **email**, and **mobile push** (iOS/Android apps). Each notification type can be toggled independently under **Account Settings → Notifications**. Critical alerts—security login from new device, billing failure—cannot be disabled.

## Smart Notifications

**Smart mode** (default on Pro+) batches low-priority updates: instead of five emails for five comment replies, you receive one digest listing all activity on watched tasks. Urgent priority tasks and direct `@mentions` always deliver immediately.

## Watching Tasks and Boards

Click the eye icon on a task to **Watch** it—you'll receive updates on all changes except label color edits. Board **Watch** notifies you of new tasks and column moves. Watchers do not need to be assignees.

## Saved Views

Filters can be saved as named **Views** accessible from the board toolbar. Views support: assignee, label, priority, due date, custom fields, and full-text search within the board. Shared views are visible to all board members; personal views are private. Example views: "My Overdue", "Unassigned High Priority", "Sprint 14 Committed".

## Dashboard Widgets

The workspace **Dashboard** (Home → Dashboard) displays widgets: **Tasks by Status** (pie chart), **Burndown** (sprint boards), **Upcoming Due Dates** (7-day list), and **Team Workload** (tasks per assignee). Widgets refresh every 5 minutes. Business plans add custom SQL-like query widgets.

## Email Deliverability

FlowBoard sends from `notifications@flowboard.io`. Add this domain to your allowlist if emails land in spam. Custom email domains (Business+) send from `notifications@yourcompany.com` after DNS verification (SPF, DKIM, DMARC records provided in setup wizard).

## Mobile-Specific Settings

Mobile apps add **Quiet Hours** (suppress non-urgent push between configured times) and **Location-based reminders** (remind about due tasks when arriving at a saved location—opt-in only, data not shared with FlowBoard servers).
