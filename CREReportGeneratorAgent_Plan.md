# CREReportGeneratorAgent Implementation Plan

## Architecture Diagram

```text
                           +----------------------------+
                           |  Raw Excel Financial Data  |
                           +----------------------------+
                                        |
                                        v
                           +----------------------------+
                           | xls_to_xlsx_converter.py   |
                           +----------------------------+
                                        |
                                        v
         +-------------------+       +---------------------+
         | OccupancyScripts  |       | FinancialScripts    |
         +-------------------+       +---------------------+
                  |                         |
                  v                         v
         Occupancy CSVs            Financial CSVs
                  |                         |
                  +-----------+-------------+
                              |
                              v
                   generate_metrics_from_csv.py
                              |
                              v
                       Metrics CSVs
                              |
                              v
                 +--------------------------+
                 | CREReportGeneratorAgent  |
                 +--------------------------+
          +-----------+--------+-------+---------+
          | DataAggregation  | Charts | Narrative |
          +-----------+--------+-------+---------+
                              |
                              v
                Rendered HTML/PDF Report
                              |
                              v
                    Email / File Delivery
```

## Module Specification Table

| Module | Responsibilities | Inputs | Outputs | Dependencies |
|-------|-----------------|--------|---------|--------------|
| `data_loader` | Load latest occupancy, financial, and metrics CSVs from `Output/` directories. | File paths from configuration | Pandas DataFrames | `pandas`, `os` |
| `data_aggregator` | Aggregate multiple property datasets, join metrics, handle missing values. | DataFrames from `data_loader` | Combined DataFrame ready for visualization | `pandas`, existing scripts |
| `visualization` | Create charts (trend lines, bar charts, occupancy rates) and save as images. | Aggregated DataFrame | Image file paths or in-memory figures | `matplotlib` or `seaborn` |
| `narrative_generator` | Use LLM to generate text summary of weekly performance. | Aggregated metrics | Text paragraph(s) | API to LLM provider (e.g., OpenAI) |
| `report_template` | Jinja2 HTML template assembling tables, charts, and narrative. | Metrics data, image paths, text | Final HTML string | `jinja2` |
| `report_exporter` | Convert HTML to PDF (optional) and save to `Output/Reports`. | HTML string | HTML/PDF file path | `pdfkit` or `weasyprint` |
| `delivery_service` | Email report or copy to shared drive on schedule. | File path of final report | Delivery confirmation | `smtplib`, network credentials |
| `scheduler` | Run the agent weekly via cron or Windows Task Scheduler. | Entry point script | None | OS scheduler |
| `logging_setup` | Standardize logging across modules. | N/A | Log files under `Output/logs` | `logging` |

## Timeline Table

| Phase / Week | Milestones | Deliverables |
|-------------|-----------|--------------|
| **1. Requirements & Setup (Week 1-2)** | Analyze existing scripts, define data sources, add new dependencies to `requirements.txt`. | Environment ready, dependency list updated. |
| **2. Data Modules (Week 3-4)** | Implement `data_loader` and `data_aggregator`. Integrate with current `FinancialScripts` and `OccupancyScripts`. | DataFrames aggregated from existing outputs. |
| **3. Visualization (Week 5)** | Build `visualization` module with sample charts. | Saved chart images. |
| **4. Narrative Generation (Week 6-7)** | Integrate `narrative_generator` using chosen LLM API. | Example narrative text from sample data. |
| **5. Reporting Template (Week 8)** | Create Jinja2 HTML template and `report_exporter`. | HTML report with embedded charts. |
| **6. Delivery & Scheduling (Week 9)** | Implement `delivery_service` and scheduling mechanism. | Automated weekly report delivery. |
| **7. Testing & Logging (Week 10-11)** | Write unit tests with `pytest`, ensure logging across modules. | Test suite, log files, code formatted with `black` and checked with `flake8`. |
| **8. Deployment (Week 12)** | Deploy agent to production environment and monitor first run. | Working CREReportGeneratorAgent scheduled weekly. |

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|-----|-----------|-------|-----------|
| Sensitive financial data exposure | Medium | High | Store credentials securely, restrict file permissions, follow company data policies. |
| LLM produces incorrect or confidential text | Medium | Medium | Review narrative output, apply prompt constraints, enable human approval in early phases. |
| Inconsistent source data format | High | Medium | Validate input files, log anomalies, fallback to default values. |
| Visualization library incompatibility | Low | Low | Pin versions in `requirements.txt`, test on staging environment. |
| Email delivery failures | Medium | Medium | Retry logic, logging of send errors, option to save to shared drive. |
| Compliance with financial reporting standards | Medium | High | Ensure calculations follow GAAP, keep audit trail of scripts and outputs. |

