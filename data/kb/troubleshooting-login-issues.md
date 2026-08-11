# Troubleshooting Login Issues

Unable to sign in to FlowBoard? This document covers password recovery, SSO failures, 2FA lockouts, and account lock scenarios.

## Password Reset

Click **Forgot password** on the login page and enter your email. Reset links expire after 60 minutes and can only be used once. If you don't receive the email within 5 minutes, check spam and verify you're using the email associated with your workspace invite. SSO-only accounts do not have passwords—use your identity provider's login instead.

## SSO and Google/Microsoft Login

**Error SSO-401**: Your identity provider rejected the login. Confirm your account exists in the IdP directory and that FlowBoard is assigned as an authorized application. Okta admins should verify the SAML ACS URL: `https://app.flowboard.io/auth/saml/callback`.

**Error SSO-403**: Your email domain isn't allowed on this workspace. Contact your workspace Admin to add your domain to the allowlist or invite you explicitly.

Google and Microsoft social login creates a FlowBoard account on first sign-in—linking to an existing email/password account requires verifying both emails under **Account → Linked Logins**.

## Two-Factor Authentication Lockout

Lost authenticator access? Use a backup code at the 2FA prompt. No backup codes? Workspace Owners can reset 2FA for members on Business plans via **Team → [user] → Reset 2FA**. Individual users without Owner support must contact support@flowboard.io with government-issued ID for manual verification (24–48 hour turnaround).

## Account Locked (FB-AUTH-429)

Five failed password attempts within 15 minutes trigger a 30-minute lockout. SSO logins are unaffected. Enterprise workspaces can configure stricter lockout policies.

## Browser and Cookie Issues

FlowBoard requires third-party cookies for SSO in embedded browsers (Slack, Teams). If login loops indefinitely, try a standalone browser or enable cookies for `flowboard.io`. Clear site data only as a last resort—it logs you out of all sessions.

## Session Expired on Mobile

Mobile sessions expire after 90 days of inactivity. Re-authenticate with biometrics or password. **Remember this device** extends SSO session length to 30 days.
