# Quant Starter 📊

A lightweight, standardized Python project skeleton designed for quantitative finance analysis.

This project provides foundational tools for:
- Data I/O operations (CSV handling)
- Basic quantitative metrics (Mean, Volatility, Max Drawdown)
- **Data quality inspection** (detecting missing values, logical errors, outliers)
---

## 📁 Project Structure

```text
quant_starter/
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
│
├── data/
│   ├── raw/                    # Raw data files
│   │   ├── sample_prices.csv       # Simple price data
│   │   ├── dirty_stock_data.csv    # Test data with errors
│   │   └── clean_stock_data.csv    # Clean OHLCV data
│   └── processed/              # Processed data (generated)
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── io_utils.py             # File I/O utilities
│   ├── metrics.py              # Quantitative metrics
│   └── data_checker.py         # Data quality inspector
│
├── tests/
│   ├── __init__.py
│   ├── test_metrics.py         # Tests for metrics
│   └── test_checker.py         # Tests for data checker
│
└── scripts/
    ├── run_basic_report.py     # Basic analysis report
    └── check_my_data.py        # Data quality check script
    
    
🚀 Getting Started

1. Prerequisites

Python 3.8 or higher
pip (Python package manager)

2. Installation

# Clone the repository
git clone <repository-url>
cd quant_starter

# Install dependencies
pip install -r requirements.txt

3. Verify Installation

# Run all tests
pytest tests/ -v

📊 Module 1: Basic Metrics

python scripts/run_basic_report.py

Features
Function	Description
mean(x)	Calculate arithmetic mean
std(x)	Calculate standard deviation (population)
max_drawdown(nav)	Calculate maximum drawdown from NAV series

Sample Output
==================================================
        📊 Basic Quantitative Analysis Report
==================================================

📂 Loading Data: data/raw/sample_prices.csv
   Total records: 10

📊 Return Statistics:
   Trading Days: 9
   Avg Daily Return: 1.2877%
   Volatility:       2.2067%

💰 NAV Analysis:
   Total Return: 12.00%
   Max Drawdown: 4.55%
   
Max Drawdown Algorithm
The implementation uses an efficient O(N) single-pass algorithm:

def max_drawdown(nav_series):
    max_dd = 0.0
    peak = nav_series[0]
    
    for nav in nav_series:
        if nav > peak:
            peak = nav
        drawdown = (peak - nav) / peak
        if drawdown > max_dd:
            max_dd = drawdown
    
    return max_dd
    
🔍 Module 2: Data Quality Checker
Purpose
Detect common data quality issues in OHLCV (Open, High, Low, Close, Volume) financial data before using it for analysis or backtesting.

# Check default test file
python scripts/check_my_data.py

# Check a specific file
python scripts/check_my_data.py path/to/your/data.csv

Checks Performed
Category	Check	Description
Integrity	Missing Values	Detects NaN/NULL values in any column
Integrity	Duplicate Dates	Finds repeated date entries
Logic	High < Low	Impossible: high price below low price
Logic	Price Range	Open/Close should be within [Low, High]
Logic	Negative Values	Prices and volume cannot be negative
Continuity	Date Gaps	Gaps larger than 3 days (possible missing data)
Outliers	Extreme Moves	Daily returns exceeding ±10%

Sample Output

============================================================
        📋 DATA QUALITY REPORT
============================================================

📊 BASIC INFO
----------------------------------------
   Total Rows: 20

🔍 MISSING VALUES
----------------------------------------
   open: 1 missing
   close: 1 missing

📅 DUPLICATE DATES
----------------------------------------
   ❌ 1 duplicate date(s) found

⚠️  LOGICAL CONSISTENCY
----------------------------------------
   High < Low errors:     1
   Price out of range:    1
   Negative values:       2
   Total logical errors:  4

📆 DATE CONTINUITY
----------------------------------------
   Gaps > 3 days:   1
   Max gap (days):  7

📈 EXTREME PRICE MOVES (>10%)
----------------------------------------
   Count: 2 day(s)

============================================================
❌ RESULT: 12 issue(s) found. Please review.
============================================================

Programmatic Usage

import pandas as pd
from src.data_checker import DataQualityChecker

# Load your data
df = pd.read_csv('your_data.csv')

# Create checker and run
checker = DataQualityChecker(df)
report = checker.run_all_checks()

# Print formatted report
checker.print_report()

# Access individual results
print(f"Missing values: {report['missing_values']}")
print(f"Logical errors: {report['logical_errors_total']}")

Report Dictionary Structure

{
    "total_rows": 1000,
    "missing_values": {"close": 2, "volume": 1},
    "duplicate_dates": 0,
    "high_low_errors": 1,
    "price_range_errors": 2,
    "negative_values": 0,
    "logical_errors_total": 3,
    "large_gaps": 1,
    "max_gap_days": 7,
    "extreme_moves": 5
}

🧪 Testing

Run All Tests
pytest tests/ -v

Run Specific Test File

# Test metrics module
pytest tests/test_metrics.py -v

# Test data checker module
pytest tests/test_checker.py -v

Test Coverage Summary
Module	Tests	Coverage
metrics.py	14	mean, std, max_drawdown
data_checker.py	18	All check functions
Total	32

📝 OHLCV Data Format

The data checker expects CSV files with these columns:

Column	Type	Description
date	string/date	Trading date (YYYY-MM-DD)
open	float	Opening price
high	float	Highest price of the day
low	float	Lowest price of the day
close	float	Closing price
volume	int/float	Trading volume

Example

date,open,high,low,close,volume
2024-01-01,100.00,105.00,99.00,103.00,1000000
2024-01-02,103.00,108.00,102.00,106.00,1100000

⚠️ Important Notes
Standard Deviation
This project uses Population Standard Deviation (dividing by n), not Sample Standard Deviation (n-1).

Vectorized Operations
All data processing uses Pandas vectorized operations for performance. No row-by-row iteration (iterrows()) is used.

# ✅ Correct (fast)
errors = df[df['high'] < df['low']]

# ❌ Wrong (slow)
for index, row in df.iterrows():
    if row['high'] < row['low']:
        ...
        
# ✅ Correct (fast)
errors = df[df['high'] < df['low']]

# ❌ Wrong (slow)
for index, row in df.iterrows():
    if row['high'] < row['low']:
        ...
        
🛠️ Development Log
Version	Task	Description
v0.1	L0-Task1	Project skeleton, metrics, basic report
v0.2	L0-Task2	Data quality checker with tests

📄 License
MIT License


