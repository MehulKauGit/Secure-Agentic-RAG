# Security Incident Response Standard Operating Procedure (SOP)

## 1. Incident Classification
- **P1 (Critical)**: Active breach, uncontained ransomware, data exfiltration in progress.
- **P2 (High)**: Compromised service account, critical unpatched vulnerability actively targeted.
- **P3 (Medium)**: Phishing email detected with low click rate, isolated malware blocked by EDR.
- **P4 (Low)**: Minor policy violations, port scans.

## 2. Notification Protocols
- For P1/P2 incidents, notify the Security Operations Center (SOC) hotline immediately at ext. 4433 or page `soc-duty@globalcorp.internal`.
- Do not attempt to reboot or power off compromised virtual machines unless authorized by the Incident Commander (preserves volatile memory for forensics).

## 3. Communication Safeguards
- All incident-related chat must occur within designated `#incident-war-room-private` Slack channels.
- External notifications to regulators and affected parties are exclusively handled by Legal and Communications within 72 hours of confirmation.
