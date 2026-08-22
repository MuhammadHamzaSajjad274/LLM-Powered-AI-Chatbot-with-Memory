# Slack Integration

FlowBoard's Slack integration connects workspace notifications and task actions to your Slack channels. Install from **Settings → Integrations → Slack** or the Slack App Directory.

## Setup and Permissions

The FlowBoard Slack app requests permissions to: post messages, read channel list, respond to slash commands, and unfurl FlowBoard links. A workspace Admin must approve the OAuth install. After connecting, map FlowBoard workspaces to Slack teams—one FlowBoard workspace per Slack workspace on Pro; multiple mappings on Business.

## Notifications

Configure per-board notification rules: post to `#channel` when tasks move to **Done**, when due dates pass, or when `@mentions` occur. Notification messages include task title, board name, assignee, and **Open in FlowBoard** button. Reduce noise with digest mode (hourly batch) per channel.

## Slash Commands

Type `/flowboard create [title]` in any channel to create a task in the default board's Backlog. `/flowboard search [query]` returns top three matching tasks. `/flowboard link [task-url]` unfurls card details in channel. Commands require the user to have linked their FlowBoard account via `/flowboard connect`.

## Link Unfurling

Pasting a FlowBoard task URL in Slack displays a rich preview with status, assignee, and due date. Private board links unfurl only for users with board access—others see "You don't have access to this task."

## Troubleshooting

**Integration disconnected**: Re-authorize under Integrations—Slack tokens expire if the installing admin leaves the Slack workspace. **Missing notifications**: Verify the FlowBoard bot is invited to the target channel (`/invite @FlowBoard`). **Duplicate messages**: Check for overlapping automation and Slack notification rules on the same trigger.

## Removing the Integration

Disconnecting revokes the OAuth token immediately. Existing unfurled links continue working; automations posting to Slack will fail with error `FB-SLACK-401` until reconnected or updated.
