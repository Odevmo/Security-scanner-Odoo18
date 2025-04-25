# Odoo Security Scanner Suite

## Overview

**Odoo Security Scanner Suite** is a developer-friendly and admin-focused module for Odoo that helps assess the security posture of your Odoo instance. It provides automated diagnostics on critical security configurations and summarizes the results in a clear, actionable report.

## Features

### 🔐 Core Security Checks
- **Master Password Validation**: Detects whether a master password is configured.
- **HTTPS Enforcement**: Confirms secure HTTP (HTTPS) usage for your Odoo instance.
- **Access Rule Verification**: Ensures all non-core models have defined access control rules with readable output.
- **Logging Setup Check**: Validates whether logging levels are configured.
- **Database Filtering**: Verifies the presence of a database filter.
- **Database Listing Control**: Checks if open database listing is disabled.

### 🛠️ Scan Management
- One-click scan initiation from the UI.
- Real-time scan progress with clear success/failure indicators.
- Automatically generated scan names for easy traceability.
- All output is verbose by default, eliminating toggles and confusion.

### 🛝 UI Integration
- Custom form and list views.
- Seamless integration with Odoo’s menu system under the "Security Scan" section.

## Installation

1. Clone or copy the `security_scanner_suite` directory into your Odoo `addons` path.
2. Restart your Odoo server.
3. Go to the Apps menu, update the app list, and install the **Security Scanner Suite**.

## Usage

1. Navigate to **Security Scanner → Scans**.
2. Click **Create** to generate a new scan record.
3. Hit **Run Scan**.
4. Review the results, all displayed in a detailed, readable format under **Scan Results**.

---

## Roadmap

We’re building a forward-thinking security layer for Odoo. Here’s where we’re heading:

### ♻️ Short-Term Enhancements
- **Scheduled Scans**: Automate security checks on a periodic basis.
- **Scan State Improvements**: Better tracking of ongoing and completed scans to optimize UI visibility.

### 🛡️ Mid-Term Goals
- **Custom Check Builder**: Let users define organization-specific checks.
- **Detailed Rule Audit**: Deeper access control coverage with rule source tracking.
- **Enhanced Reporting**: Exportable and filterable scan summaries for audits and compliance.

### 🤖 Long-Term Vision
- **LLM-Driven Insight**: Use AI to interpret results, recommend mitigations, and generate security audit summaries.
- **CVE Detection Engine**: Cross-reference your Odoo version against a live CVE database.
- **Module Code Scanner**: Analyze custom or third-party modules for common security risks:
  - SQL injections
  - XSS vulnerabilities
  - Unsafe file access patterns
  - Misconfigured access groups

---

## License

[LGPL-3.0](https://www.gnu.org/licenses/lgpl-3.0.en.html)

## Contributing

We welcome your contributions! Create an issue, open a pull request, or suggest enhancements to improve security for the Odoo ecosystem.

