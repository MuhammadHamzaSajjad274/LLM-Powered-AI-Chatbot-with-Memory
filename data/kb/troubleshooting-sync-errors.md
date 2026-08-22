# Troubleshooting Sync Errors

FlowBoard syncs changes in real time across web, desktop, and mobile clients. When sync fails, you may see a banner reading **"Changes couldn't sync — retrying"** or error code **FB-SYNC-102**. This guide covers common causes and fixes.

## Check Network and Status

First verify your internet connection and visit status.flowboard.io for platform incidents. FlowBoard requires WebSocket connectivity to `wss://sync.flowboard.io` on port 443. Corporate proxies that strip WebSocket headers cause persistent sync failures—whitelist the domain or use the desktop app's offline mode.

## Force Refresh

Press `Cmd/Ctrl + Shift + R` to hard refresh the browser tab. On mobile, pull down on the board list to trigger a manual sync. The desktop app offers **Help → Force Sync** which clears the local cache and re-downloads board state.

## Conflict Resolution

If two users edit the same field simultaneously, FlowBoard applies **last-write-wins** for most fields but merges comment threads. Unresolvable conflicts show a **Merge Required** dialog on task open—choose which version to keep for title and description. Conflict events appear in the task activity log.

## Error FB-SYNC-102: Stale Session

This error means your auth token expired mid-session. Log out and log back in. If using SSO, ensure your IdP session hasn't timed out. Enterprise admins can extend token TTL under **Security → Session Policy** (max 24 hours).

## Error FB-SYNC-204: Payload Too Large

Attachments or descriptions exceeding 10 MB per save attempt trigger this error. Split large descriptions or upload files via **Attachments** (which use chunked upload) rather than pasting base64 content.

## Offline Mode

The desktop app caches the last 30 days of assigned tasks for offline editing. Changes queue locally and sync on reconnect. Queued edits older than 7 days are discarded with a warning email. Mobile offline is read-only except for checklist toggles.

## Contact Support

If sync fails for 30+ minutes despite these steps, export browser console logs (`Help → Diagnostic Report`) and attach to a support ticket. Pro and Business plans receive priority sync incident response.
