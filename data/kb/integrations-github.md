# GitHub Integration

Connect GitHub repositories to FlowBoard boards to link pull requests, branches, and commits to tasks. Available on Pro plan and above.

## Connecting Repositories

Navigate to **Board Settings → Integrations → GitHub** and authenticate with GitHub OAuth. Select repositories to link—each board supports up to 10 repos. FlowBoard registers a webhook on each repo for push, pull request, and issue events.

## Linking PRs to Tasks

Include `FB-1234` (task ID) in a PR title or description to auto-link. Alternatively, paste the task URL in a PR comment and FlowBoard bot replies with confirmation. Linked PRs appear in the task detail panel with status badge (Open, Merged, Closed).

## Automation: PR Merged → Done

Enable the template automation **When PR merged, move task to Done** under Automations. Optionally require all checklist items complete before auto-moving. If the PR closes without merge, the task moves to **Cancelled** column when configured.

## Branch Naming

FlowBoard suggests branch names `feature/FB-1234-short-description` when creating branches from the task panel (requires GitHub CLI or web flow). Branch links display on the task activity timeline.

## Commit Messages

Commits referencing `FB-1234` in the message appear in task activity. Squash merges only retain the squash commit message—ensure it includes the task ID.

## Permissions

The connecting user must have GitHub write access to linked repos. FlowBoard bot actions (posting PR comments) use the installing user's token—if they leave the organization, reconnect with a service account (Enterprise) or another admin.

## Troubleshooting

**Webhook delivery failures**: Check repo Settings → Webhooks for `flowboard.io` delivery errors. **Missing PR links**: Task ID must match exactly—project-scoped IDs like `PROJ-123` require enabling **Custom ID prefixes** in board settings. **Rate limits**: GitHub API rate limits may delay sync up to 5 minutes during heavy activity.
