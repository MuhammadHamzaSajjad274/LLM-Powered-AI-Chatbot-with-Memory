# Account Settings

Your FlowBoard account settings control profile information, authentication, notification preferences, and connected apps. Access them via the avatar menu → **Account Settings**.

## Profile and Preferences

Update display name, profile photo, job title, and timezone. Timezone affects due date reminders and automation schedules. Language options include English, Spanish, French, German, and Japanese (UI only—user-generated content is not translated).

## Authentication and Security

FlowBoard supports email/password login and Google, Microsoft, and Okta SSO (Business plan+). Enable **Two-Factor Authentication (2FA)** via authenticator app (TOTP)—required for Admin and Owner roles on Business plans. Backup codes generate at enrollment; store them securely.

Password requirements: minimum 12 characters, at least one uppercase, lowercase, and number. Passwordless magic links expire after 15 minutes. Session timeout defaults to 30 days; Enterprise can enforce shorter idle timeouts.

## Notification Preferences

Configure email, in-app, and mobile push notifications independently for: task assignments, mentions, due date reminders, board invitations, and automation failures. **Digest mode** bundles non-urgent notifications into a single daily email at 8:00 AM local time.

## Connected Apps

View and revoke OAuth connections to Slack, GitHub, Google Calendar, and Zapier. Revoking access takes effect immediately; automations using that connection will fail until reconnected.

## Data Export and Account Deletion

Request a full data export (JSON + attachments ZIP) under **Privacy → Export My Data**—delivered within 72 hours. Account deletion is permanent after a 14-day grace period. Workspace Owners must transfer ownership before deleting their account.

## API Tokens

Personal API tokens for scripting are available on Pro plan and above. Tokens inherit your permission level, expire after 90 days by default, and can be scoped to read-only or read-write.
