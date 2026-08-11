# Team Management

Workspace administrators manage members, roles, groups, and access policies from **Settings → Team**. This guide covers invitations, role capabilities, groups, and offboarding.

## Roles and Permissions

| Role | Create boards | Manage billing | Delete workspace |
|------|--------------|----------------|------------------|
| Viewer | No | No | No |
| Member | Yes | No | No |
| Admin | Yes | No | No |
| Owner | Yes | Yes | Yes |

Admins can invite/remove members, configure automations, and set board permissions. Only Owners access billing and can delete the workspace. Members cannot change another user's role unless granted **People Manager** custom permission (Business plan).

## Inviting Members

Send invites individually or bulk-upload a CSV (email, role columns). Pending invites appear in the team table with **Resend** and **Revoke** actions. Domain allowlisting (Business+) restricts joins to `@yourcompany.com` emails.

## Groups

Groups bundle members for board assignment and notifications. Example: `@platform-engineering` group assigned to the Infrastructure board. Groups do not replace roles—a group member still needs at least Member role to edit tasks.

## Offboarding

When removing a member, FlowBoard prompts to **Reassign open tasks**. Unassigned tasks remain on boards with a "Former member" badge. Removed members lose access immediately; their comments and activity history are preserved for audit purposes.

## Audit Log (Business+)

The audit log records member invites, role changes, board permission updates, and failed login attempts. Logs export to CSV and retain for 365 days. SIEM integration available via webhook on Enterprise.

## Guest Access

Guests are external collaborators with Viewer or Member role on specific boards only—they do not appear in the workspace directory and cannot create boards. Guest count limits: 10 on Pro, unlimited on Business.
