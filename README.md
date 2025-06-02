# AM Model Extraction

A Python-based automation toolkit for extracting and processing asset management model data, focusing on financial analysis and occupancy reporting for real estate portfolios.

## 🏗️ Project Structure

```
AM Model Extraction/
├── Data/                          # Raw data files (excluded from repo)
│   ├── _ARGUS CF/                # ARGUS cash flow data
│   ├── _MODEL/                   # Model files
│   ├── _RENT ROLL/              # Rent roll data
│   ├── _TEST DATA/              # Test datasets
│   └── Celina Hampshire/        # Property-specific data
├── FinancialScripts/            # Financial analysis scripts
│   └── Output/
│       └── METRICS/             # Financial metrics output
├── OccupancyScripts/            # Occupancy analysis scripts
├── Output/                      # Generated reports and analysis
│   ├── FINANCIALS/             # Financial reports
│   ├── METRICS/                # Calculated metrics
│   ├── OCCUPANCY/              # Occupancy reports
│   └── TEST/                   # Test outputs
├── tools/                       # Utility scripts and tools
├── xls_to_xlsx_converter.py    # Excel format converter
└── README.md                   # This file
```

## 🚀 Features

- **Excel Format Conversion**: Automated conversion from XLS to XLSX format
- **Financial Analysis**: Scripts for processing financial data and generating metrics
- **Occupancy Reporting**: Tools for analyzing and reporting occupancy data
- **Data Pipeline**: Streamlined workflow for data ingestion and transformation
- **Modular Design**: Separate scripts for different analysis types

## 📋 Prerequisites

- Python 3.7+
- Required Python packages (see requirements.txt)
- Excel files in supported formats

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/melanson633/model_extraction.git
cd model_extraction
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your data directory structure as shown above

## 📖 Usage

### Excel Format Conversion
```python
python xls_to_xlsx_converter.py
```

### Financial Analysis
Navigate to the `FinancialScripts/` directory and run the appropriate analysis scripts.

### Occupancy Analysis
Use scripts in the `OccupancyScripts/` directory for occupancy-related calculations.

## 📊 Data Security

This project handles sensitive financial data. The following files and directories are excluded from version control:
- All Excel files (*.xlsx, *.xls)
- CSV files (*.csv)
- Data/ directory contents
- Output/ directory contents

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is private and proprietary. All rights reserved.

## 📧 Contact

For questions or support, please contact the repository owner.

---

**Note**: This project contains proprietary financial analysis tools. Please ensure compliance with your organization's data handling policies when using these scripts. 
## 🧪 Running Tests

This repository uses `pytest` for unit testing. After installing the dependencies, run the test suite with:

```bash
pytest
```

Tests are located in the `tests/` directory and cover utility functions used by the occupancy scripts.


