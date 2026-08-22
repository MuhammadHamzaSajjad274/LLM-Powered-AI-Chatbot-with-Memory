# Automations

FlowBoard Automations reduce repetitive board maintenance by executing actions when triggers occur. Automations are configured per board under **Board Settings → Automations** and require Member role or higher to create.

## Trigger Types

Available triggers include: **Card moved to column**, **Card created**, **Due date reached**, **Label added**, **Assignee changed**, **Comment contains keyword**, and **Scheduled (cron)**. Scheduled automations run at most once per hour and use the workspace timezone.

## Action Types

Actions include: **Move card to column**, **Assign to user**, **Add/remove label**, **Post comment**, **Send Slack notification**, **Create linked card on another board**, **Set due date offset** (e.g., +3 days), and **Webhook POST**. Multiple actions can chain in a single automation; they execute sequentially.

## Example: Auto-assign Review

Trigger: Card moved to column **Review**. Action: Assign to `@review-lead` and post comment "Ready for review—please respond within 24 hours." This pattern is available as a one-click template in the Automation Gallery.

## Example: Stale Task Escalation

Trigger: Scheduled daily at 9:00 AM. Condition: Card in **In Progress** with no activity for 5 days. Action: Add label `stale`, notify assignee via email, and move to **Needs Attention** column if configured.

## Limits by Plan

Free plan: 3 automations per board. Pro plan: 25 automations per board. Business plan: unlimited. Automations that fail three consecutive times are automatically disabled and the board admin receives an alert with the error payload.

## Debugging Automations

Each automation maintains an execution log (last 30 days) showing trigger timestamp, matched card, actions run, and success/failure status. Error code `FB-AUTO-500` indicates webhook timeout (10 second limit).
