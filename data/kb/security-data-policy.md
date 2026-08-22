# Security and Data Policy

FlowBoard is committed to protecting customer data. This document summarizes encryption, compliance, data residency, retention, and incident response practices.

## Encryption

Data in transit uses TLS 1.2 or higher. Data at rest is encrypted with AES-256 on AWS infrastructure. Database backups are encrypted and stored in a separate region from primary data. Customer-uploaded attachments inherit the same encryption standards.

## Compliance

FlowBoard maintains SOC 2 Type II certification (annual audit, report available to Business and Enterprise customers under NDA). GDPR compliance includes Data Processing Agreement (DPA), right to erasure, and EU Standard Contractual Clauses for data transfers. HIPAA BAA available on Enterprise with configured controls.

## Data Residency

Default data storage is US-East (AWS us-east-1). Business customers can request EU residency (Frankfurt, eu-central-1) at workspace creation—migration after creation requires support assistance. Enterprise supports dedicated single-tenant deployments in customer-specified regions.

## Data Retention

Active workspace data persists until account deletion. Deleted tasks move to **Trash** for 30 days before permanent purge. Audit logs retain 365 days on Business, configurable up to 7 years on Enterprise. Backups retain 35 days for disaster recovery.

## Access Controls

FlowBoard employees access production systems on a least-privilege basis with MFA required. Production access is logged and reviewed quarterly. Penetration testing occurs annually by third-party firms; summary reports available to Enterprise customers.

## Incident Response

Security incidents are triaged within 1 hour of detection. Customers affected by a confirmed breach receive notification within 72 hours per GDPR requirements. Report vulnerabilities to security@flowboard.io—our bug bounty program awards $100–$5,000 for valid findings.

## Customer Responsibilities

Customers control access via roles, SSO, and 2FA enforcement. FlowBoard recommends enabling SSO with 2FA for all Admin and Owner accounts. Do not share API tokens or store them in public repositories.

## Subprocessors

Current subprocessors include AWS (hosting), SendGrid (email), and Stripe (billing). The full list updates at flowboard.io/legal/subprocessors with 30-day advance notice for new additions.
