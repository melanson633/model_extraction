# Repo Explorer → Claude Code Skill Miner Report

## Pass 1: Structural Survey (Broad Discovery)

### Overall assessment of CRE finance/accounting relevance
This repository is **highly relevant** to CRE finance/accounting workflows. It is a Python automation toolkit centered on extracting occupancy and financial data from Excel cash flow models, normalizing categories/properties with mapping dictionaries, and generating portfolio metrics (including forward NOI, basis, and debt balances).

### Structural Inventory (organized by directory)

#### `/` (repository root)
- `README.md` — Project overview, directory conventions, usage entry points for conversion/financial/occupancy scripts, and pytest guidance.
- `requirements.txt` — Python dependency list for pandas/numpy/openpyxl/xlrd/xlsxwriter/pytest.
- `xls_to_xlsx_converter.py` — Windows COM automation script that batch-converts `.xls` to `.xlsx`, logs actions, and deletes originals after successful conversion.
- `CREReportGeneratorAgent_Plan.md` — Design plan for a future report-generation agent (data loader/aggregator/charts/narrative/template/export/delivery/scheduler).
- `CONTRIBUTING.md` — Basic contribution workflow (branch/commit/PR process).
- `LICENSE` — Proprietary/private rights statement.

#### `/tools`
- `tools/copy_q1_reports.py` — CLI tool that recursively scans source directories and copies files matching `*Q1 2025 Report*` (xls/xlsx/xlsm) into a destination folder with optional verbose summary.

#### `/FinancialScripts`
- `FinancialScripts/CATEGORIES_AM_Model_Extract.py` — Core extractor that reads each model workbook, finds the `Categories` anchor and date columns, stops at `Change in Cash`, maps categories via dictionary CSV, and exports normalized long-format financial CSV rows.
- `FinancialScripts/COMBINE_AND_FILTER_FINANCIALS.py` — Combines financial CSVs, remaps properties via dictionary CSV, filters to target debt-service categories and date threshold, then writes timestamped combined output.
- `FinancialScripts/COMBINE_AND_PROCESS_NOI.py` — Combines occupancy outputs, remaps properties via NOI dictionary, selects `PROPERTY/MONTH/F12 NOI`, and writes timestamped NOI output.
- `FinancialScripts/generate_metrics_from_csv.py` — Calculates monthly `F12 NOI`, cumulative `BASIS`, and cumulative `DEBT BALANCE` from normalized financial input CSVs.
- `FinancialScripts/REBUILD_category_list_from_output.py` — Scans output CSVs to regenerate a unique category list seed file for dictionary maintenance.
- `FinancialScripts/CATEGORY_sampling.py` — Samples and compiles unique category values from model workbooks to bootstrap mapping-dictionary creation.
- `FinancialScripts/PROPERTY_output_sampling.py` — Extracts unique property names from financial outputs for property mapping dictionary maintenance.
- `FinancialScripts/NOI_PROPERTY_output_sampling.py` — Extracts unique property names from occupancy/NOI outputs for NOI property mapping dictionary maintenance.
- `FinancialScripts/__init__.py` — Package marker.

#### `/OccupancyScripts`
- `OccupancyScripts/OCCUPANCY_AM_Model_Extract.py` — Occupancy extractor: reads cash flow sheet, finds occupancy anchors, parses dates/numeric/percent values, and exports occupancy CSV.
- `OccupancyScripts/OCCUPANCY_v2_AM_Model_Extract.py` — Version with improved `.xls/.xlsx` engine handling and explicit file list configuration.
- `OccupancyScripts/OCCUPANCY_v3_AM_Model_Extract.py` — Extended extractor that adds `F12 NOI`, `TENANT IMPROVEMENTS`, and `LEASING COMMISSIONS`, with cutoff filtering and forward-looking NOI computation.
- `OccupancyScripts/__init__.py` — Package marker.

#### `/tests`
- `tests/test_occupancy_utils.py` — Unit tests for key parsing helpers (`extract_property_name`, month parsing, numeric parsing, percentage parsing).

### Pass 1 findings against requested discovery checklist
1. **Languages/frameworks/libraries:** Python scripts using pandas/numpy/openpyxl/xlrd/dateutil/win32com/csv/logging/argparse/pathlib.
2. **Data models/schemas/configs/datasets:** Repeated long-form schema `CATEGORY, MONTH, AMOUNT, PROPERTY`; occupancy schema with SF/%/NOI fields; mapping dictionary CSV conventions (`MODEL_UniqueCategory`, `EXTRACTION_MAPPING`, `MODEL_UniqueProperty`, `DebtTerms_Property`).
3. **Templates/prompt/instruction docs:** `CREReportGeneratorAgent_Plan.md` includes a module blueprint and roadmap for report automation.
4. **Automation/parsers/converters/ETL logic:** Multiple batch extract/transform/combine scripts + Excel format converter + file copy utility.
5. **Financial calculation/business logic:** Explicit F12 NOI windowing, basis category accumulation/sign flip, debt balance accumulation, category/date/property filters.
6. **API integrations/connectors:** No production API/webhook integration in current code; only planned LLM/email/export components in planning doc.
7. **PDF/doc processing/OCR:** None in current implementation; PDF export appears only in planning document.
8. **Reusable utilities:** robust parsing functions (date/numeric/percent), anchor-row discovery, timestamped output naming, mapping loaders, warning/logging patterns.

---

## Pass 2: Pattern Analysis Report (Top Components)

| # | Component | What it does | CRE finance/accounting applicability | Modularity | Dependencies | Embedded domain knowledge |
|---|---|---|---|---|---|---|
| 1 | `FinancialScripts/CATEGORIES_AM_Model_Extract.py` | Extracts category/month/amount/property rows from model workbooks using anchors and mapping dictionary. | Strong fit for monthly close, budgeting/reforecast base-data normalization, and lender/investor package prep. | **HIGH** | openpyxl, mapping CSV, input folder conventions. | Anchor semantics (`Categories` to `Change in Cash`), normalized schema, category remap pattern. |
| 2 | `OccupancyScripts/OCCUPANCY_v3_AM_Model_Extract.py` | Extracts occupancy rows plus NOI/TI/LC and computes forward 12-month NOI from source cash flow sheets. | Directly useful for occupancy monitoring, asset management modeling, and debt/lender NOI tracking. | **HIGH** | pandas/numpy/dateutil/openpyxl/xlrd; anchor labels in source files. | Anchor-based extraction rules, F12 NOI logic, post-2024 cutoff rule, optional field defaults. |
| 3 | `FinancialScripts/generate_metrics_from_csv.py` | Builds property-month metrics dataset with F12 NOI, BASIS, and DEBT BALANCE from normalized financial CSVs. | High value for covenant tracking, investor updates, and portfolio dashboard inputs. | **HIGH** | pandas/numpy; category naming consistency. | Basis category set definition, cumulative finance logic, NOI forward window treatment. |
| 4 | `FinancialScripts/COMBINE_AND_FILTER_FINANCIALS.py` | Combines all financial CSVs; remaps property names; filters by category/date; outputs timestamped aggregate. | Strong fit for debt service reporting and lender data package assembly. | **MEDIUM-HIGH** | csv/os/datetime + property mapping CSV. | Target debt categories and post-threshold date filtering policy. |
| 5 | `FinancialScripts/COMBINE_AND_PROCESS_NOI.py` | Consolidates occupancy outputs into a clean NOI file with mapped property names. | Useful for standardizing NOI feeds into debt terms or covenant models. | **MEDIUM-HIGH** | csv/os/datetime + NOI mapping CSV. | Required output schema (`PROPERTY, MONTH, F12 NOI`) and remapping conventions. |
| 6 | `FinancialScripts/REBUILD_category_list_from_output.py` | Rebuilds unique category dictionary seed from generated financial outputs. | Useful governance workflow for maintaining chart-of-accounts style mappings over time. | **HIGH** | csv/os; output directory conventions. | Naming of master mapping key (`MODEL_UniqueCategory`) and iterative curation workflow. |
| 7 | `FinancialScripts/CATEGORY_sampling.py` | Samples category labels from source workbooks to aid dictionary creation/QA. | Helps onboarding new properties with inconsistent category labels. | **MEDIUM** | openpyxl/csv; workbook layout assumptions. | Early-stage dictionary curation practices and dedupe patterns. |
| 8 | `FinancialScripts/PROPERTY_output_sampling.py` | Extracts unique property names from financial outputs to build property mapping tables. | Important for JV portfolio standardization across systems (e.g., lender/legal naming mismatches). | **HIGH** | csv/os/datetime. | Property-key governance, timestamped dictionary generation pattern. |
| 9 | `FinancialScripts/NOI_PROPERTY_output_sampling.py` | Extracts unique property names from NOI/occupancy outputs for separate mapping maintenance. | Supports multi-feed normalization where NOI feed naming differs from GL/financial feeds. | **HIGH** | csv/os/datetime. | Separate mapping dictionary strategy by data feed type. |
| 10 | `tools/copy_q1_reports.py` | Recursively finds/copies report files matching naming pattern and extension list. | Applicable to period-close packet collection and audit support workflows. | **HIGH** | pathlib/shutil/os/argparse. | Period-specific naming pattern scan (`Q1 2025 Report`) and overwrite accounting. |
| 11 | `xls_to_xlsx_converter.py` | Converts legacy `.xls` files to `.xlsx` via Excel COM and logs outcomes. | Useful when vendors/lenders deliver mixed legacy files before ingestion. | **MEDIUM** (Windows-bound) | Windows + Excel + pywin32 COM. | Controlled conversion + delete-original-on-success policy. |
| 12 | `OccupancyScripts/OCCUPANCY_AM_Model_Extract.py` | Baseline occupancy extraction with fallback engine attempts and anchor parsing. | Useful as a simpler extraction template when v3 fields are not required. | **MEDIUM-HIGH** | pandas/dateutil/openpyxl/xlrd. | Core anchor map and parser utilities. |
| 13 | `OccupancyScripts/OCCUPANCY_v2_AM_Model_Extract.py` | Transitional extractor with explicit file list and extension-aware loading. | Niche use for controlled test sets and deterministic runs. | **MEDIUM** | pandas/dateutil + manual file list maintenance. | Demonstrates migration from static list to directory-driven automation. |
| 14 | `tests/test_occupancy_utils.py` | Tests parser utility correctness for date/number/percentage/property parsing. | High value as a reusable validation harness for extracted skill packages. | **HIGH** | pytest + occupancy utility imports. | Baseline quality checks for parser reliability in finance ETL contexts. |
| 15 | `CREReportGeneratorAgent_Plan.md` | Future architecture for automated report generation with visuals, narratives, and delivery. | Strategic relevance for investor reporting automation but not implemented yet. | **LOW-MEDIUM** (spec only) | Would require new modules/deps/APIs. | Workflow decomposition and risk register useful for skill scaffolding. |

### Pass 2 synthesis notes
- The strongest extractable value is not a single monolith; it is the **pipeline pattern**: `extract → normalize/map → combine/filter → compute metrics → output/governance`.
- The repository has **minimal direct AP/AR, bank rec, CAM, lease abstraction, or tax logic**; strongest alignment is in AM modeling, NOI/debt metrics, and data normalization.
- Several scripts are hardcoded to local Windows paths, but logic itself is portable if path/config layers are abstracted.

---

## Pass 3: Skill Synthesis (Exactly 5 Ranked Skill Ideas)

### 1. CRE Cash Flow Model Extractor & Normalizer
**Value Proposition:** This Skill would automate the most repetitive finance task in the repo: extracting structured monthly data out of semi-structured AM model workbooks and normalizing it into a clean long-form table. For a CRE finance team, that directly shortens monthly close/reforecast prep and reduces manual copy-paste risk across many JV properties.

**Source Components:**
- `FinancialScripts/CATEGORIES_AM_Model_Extract.py`: Anchor-driven category/date extraction and long-format output schema.
- `FinancialScripts/CATEGORY_sampling.py`: Category sampling/bootstrap pattern for dictionary curation.
- `FinancialScripts/REBUILD_category_list_from_output.py`: Governance loop to refresh and maintain category dictionaries.

**Replication Targets:** Extract the anchor-finding + date parsing + category remapping logic, then adapt paths/config into parameterized inputs. Copy the normalized output schema and unmapped logging behavior; modify hardcoded paths and sheet assumptions into user-configurable fields. Build a small validation checklist (required anchors, row counts, unmapped category report) as new Skill guidance.

**Modularity Assessment:** **HIGH.** The extractor and mapping workflow are self-contained ETL steps with clear inputs/outputs. Main boundary conditions: workbook layout drift (anchor names), dictionary CSV availability, and Excel engine compatibility.

**Proposed SKILL.md Structure:**
```yaml
name: cre-cashflow-model-extractor
description: Use when you need to parse AM model Excel files into normalized category/month/property CSVs with category mapping and unmapped-category QA.
```
- Detect workbook pattern and validate required anchors (`Categories`, `Change in Cash`, date columns).
- Run extraction into `CATEGORY, MONTH, AMOUNT, PROPERTY` output format.
- Apply mapping dictionary and produce unmapped-category exception list.
- Perform validation checks (non-empty output, date format, amount type, duplicate scans).
- Provide follow-up actions for dictionary maintenance.

**Confidence Level:** **HIGH**

---

### 2. Occupancy + Forward NOI Signal Extractor
**Value Proposition:** This Skill packages the v3 occupancy logic that captures occupancy KPIs and computes forward 12-month NOI directly from model cash flow sheets. It would accelerate lender reporting, debt monitoring, and AM performance reviews by turning raw model tabs into decision-ready monthly metrics.

**Source Components:**
- `OccupancyScripts/OCCUPANCY_v3_AM_Model_Extract.py`: Anchor extraction for occupancy + NOI/TI/LC and F12 NOI computation.
- `OccupancyScripts/OCCUPANCY_AM_Model_Extract.py`: Baseline parser helpers and fallback extraction pattern.
- `tests/test_occupancy_utils.py`: Parser quality checks and expected behavior examples.

**Replication Targets:** Copy utility parsers (`parse_month_headers`, numeric/percentage parsers, anchor finder), F12 NOI forward-window logic, and CSV schema. Modify hardcoded folders and cutoff date into parameters. Build new fallback guidance for optional anchors (`Tenant Improvements`, `Leasing Commissions`) and output completeness thresholds.

**Modularity Assessment:** **HIGH.** Logic is concentrated in one extractor family and can be packaged with minimal external coupling. Key dependencies are pandas/date parsing and consistent anchor labels.

**Proposed SKILL.md Structure:**
```yaml
name: cre-occupancy-noi-extractor
description: Use when extracting occupancy metrics and forward NOI from ARGUS/AM cash flow worksheets for portfolio reporting.
```
- Validate workbook/sheet and required anchor rows.
- Parse monthly headers and occupancy/NOI metric rows.
- Compute forward 12-month NOI safely (insufficient-history handling).
- Emit standardized occupancy + NOI dataset with QA logs.
- Run parser tests and exception reporting.

**Confidence Level:** **HIGH**

---

### 3. Debt & Covenant Feed Builder (Financial + NOI Combine)
**Value Proposition:** This Skill standardizes disparate property-level outputs into lender-ready feeds by remapping property names, applying category/date filters, and producing curated debt/NOI files. It directly addresses recurring monthly or quarterly covenant reporting pain where naming mismatches and inconsistent source feeds create manual reconciliation overhead.

**Source Components:**
- `FinancialScripts/COMBINE_AND_FILTER_FINANCIALS.py`: Debt category/date filtering + property remapping + timestamped output.
- `FinancialScripts/COMBINE_AND_PROCESS_NOI.py`: NOI feed consolidation and output schema standardization.
- `FinancialScripts/PROPERTY_output_sampling.py`: Property mapping dictionary maintenance workflow.
- `FinancialScripts/NOI_PROPERTY_output_sampling.py`: Separate NOI-property dictionary maintenance.

**Replication Targets:** Copy mapping-load/validation patterns and filtered-combine loops. Modify static target filters into configurable policy blocks (e.g., lender pack profile). Build new consistency checks to compare property coverage between financial and NOI feeds and flag unmapped entities.

**Modularity Assessment:** **MEDIUM-HIGH.** Components are cohesive but rely on external mapping CSVs and consistent input headers. Works cleanly if mapping files are included as skill assets/templates.

**Proposed SKILL.md Structure:**
```yaml
name: cre-debt-covenant-feed-builder
description: Use when preparing standardized debt-service and NOI files for lender/covenant reporting across multiple properties.
```
- Load/validate mapping dictionaries and input schemas.
- Merge financial files and enforce lender-specific category/date filters.
- Merge NOI files and normalize property keys.
- Export timestamped outputs plus unmapped-property exception logs.
- Rebuild mapping seed lists when new property names appear.

**Confidence Level:** **HIGH**

---

### 4. Asset Management Metrics Calculator (F12 NOI / BASIS / Debt Balance)
**Value Proposition:** This Skill converts normalized monthly transactions into modeling-ready KPI series used in AM and investment committee review. It can speed up reforecasting and covenant health monitoring by producing consistent, repeatable property-level metric snapshots without ad hoc spreadsheet formulas.

**Source Components:**
- `FinancialScripts/generate_metrics_from_csv.py`: Core metric engine for F12 NOI, basis accumulation, and debt balance accumulation.
- `FinancialScripts/COMBINE_AND_FILTER_FINANCIALS.py`: Upstream shaping assumptions and debt category convention.

**Replication Targets:** Copy metric formulas and category sets; modify category configuration to be user-editable (different portfolio chart-of-accounts). Build new validation blocks for missing categories, outlier month jumps, and month continuity checks.

**Modularity Assessment:** **HIGH.** Metric logic is centralized and largely independent once normalized input schema is guaranteed. Dependency boundary is mostly category naming consistency.

**Proposed SKILL.md Structure:**
```yaml
name: cre-am-metrics-calculator
description: Use when you need monthly AM metrics (forward NOI, basis, debt balance) from normalized property financial CSVs.
```
- Validate required input schema and category presence.
- Compute rolling/forward NOI and cumulative basis/debt metrics.
- Output standardized property-month metrics table.
- Run anomaly checks (missing months, missing categories, zeroed windows).
- Provide interpretation notes for finance users.

**Confidence Level:** **HIGH**

---

### 5. Period-Close File Intake & Excel Compatibility Utility
**Value Proposition:** This Skill handles operational ingestion friction: collecting period-specific report files from nested folders and converting legacy `.xls` to `.xlsx` for downstream processing. It improves reliability in month/quarter-end close cycles where files arrive from many sources in inconsistent formats.

**Source Components:**
- `tools/copy_q1_reports.py`: Recursive filename-pattern copy workflow with overwrite tracking.
- `xls_to_xlsx_converter.py`: Batch legacy-to-modern Excel conversion with logging.
- `requirements.txt`: Dependency guidance (`openpyxl`, `xlrd`, `xlsxwriter`; plus pywin32 requirement implied by converter script).

**Replication Targets:** Copy recursive search/copy and conversion flow; modify hardcoded quarter naming into parameterized period pattern (`Q[1-4] YYYY` or month-end labels). Build new preflight checks to detect Windows/Excel COM availability and fallback behavior when COM is unavailable.

**Modularity Assessment:** **MEDIUM.** Copy utility is portable; converter is Windows/Excel COM dependent, which reduces universal portability. Skill remains packageable if OS constraints are explicit.

**Proposed SKILL.md Structure:**
```yaml
name: cre-period-close-file-intake
description: Use when collecting period-end Excel packs and normalizing legacy XLS files before finance ETL workflows.
```
- Scan recursively for period-specific report naming patterns.
- Copy/organize files into intake directory with overwrite summary.
- Convert legacy `.xls` files to `.xlsx` when environment supports COM.
- Log conversion/copy exceptions and unresolved files.
- Handoff checklist for downstream extraction scripts.

**Confidence Level:** **MEDIUM-HIGH**
