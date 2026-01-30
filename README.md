# Quant Starter 📊

A lightweight, standardized Python project skeleton designed for quantitative finance analysis.

This project provides foundational tools for:
- **Data I/O**: CSV and Parquet file handling
- **Data Quality**: Detecting missing values, logical errors, outliers
- **Data Processing**: ETL pipeline with cleaning and feature engineering
- **Quantitative Metrics**: Mean, Volatility, Max Drawdown

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
│   │   ├── sample_prices.csv
│   │   ├── dirty_stock_data.csv
│   │   ├── clean_stock_data.csv
│   │   └── stock_data_dirty.csv
│   └── processed/              # Processed data (generated)
│       └── market_data.parquet
│
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration settings
│   ├── io_utils.py             # File I/O utilities
│   ├── metrics.py              # Quantitative metrics (Mean, Std, MaxDD)
│   ├── data_checker.py         # Data quality inspector
│   └── processors.py           # ETL: Cleaning & Feature Engineering
│
├── tests/
│   ├── __init__.py
│   ├── test_metrics.py         # Tests for metrics
│   ├── test_checker.py         # Tests for data checker
│   └── test_processors.py      # Tests for data processor
│
└── scripts/
    ├── run_basic_report.py     # Basic analysis report
    ├── check_my_data.py        # Data quality check script
    └── run_etl.py              # ETL pipeline runner
    
    
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
Calculate fundamental quantitative metrics.

Usage
python scripts/run_basic_report.py

Features
Function	Description	Complexity
mean(x)	Arithmetic mean	O(N)
std(x)	Standard deviation (population)	O(N)
max_drawdown(nav)	Maximum drawdown from NAV series	O(N)
Max Drawdown Algorithm
Efficient single-pass O(N) implementation:
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
Detect common data quality issues in OHLCV financial data.

Usage

# Check default test file
python scripts/check_my_data.py

# Check a specific file
python scripts/check_my_data.py path/to/your/data.csv

Checks Performed
Category	Check	Description
Integrity	Missing Values	Detects NaN/NULL values
Integrity	Duplicate Dates	Finds repeated date entries
Logic	High < Low	Impossible price relationship
Logic	Price Range	Open/Close within [Low, High]
Logic	Negative Values	Prices/volume cannot be negative
Continuity	Date Gaps	Gaps larger than 3 days
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

⚠️  LOGICAL CONSISTENCY
----------------------------------------
   High < Low errors:     1
   Total logical errors:  4

============================================================
❌ RESULT: 12 issue(s) found. Please review.
============================================================

🏭 Module 3: Data Processor (ETL Pipeline)
Clean raw data and generate technical features for strategy research.

Usage
# Run with default paths
python scripts/run_etl.py

# Specify custom paths
python scripts/run_etl.py --input data/raw/my_data.csv --output data/processed/output.parquet

# Run with verification
python scripts/run_etl.py --verify

ETL Pipeline Flow

┌─────────────────────────────────────────────────────────────┐
│  EXTRACT                                                    │
│  └── Read CSV file                                          │
├─────────────────────────────────────────────────────────────┤
│  TRANSFORM                                                  │
│  ├── Clean: Forward Fill (ffill) → Backward Fill (bfill)    │
│  ├── Clean: Remove duplicate dates                          │
│  ├── Feature: Daily Return                                  │
│  ├── Feature: MA5 (5-day Moving Average)                    │
│  ├── Feature: MA20 (20-day Moving Average)                  │
│  └── Feature: Vol_20 (20-day Rolling Volatility)            │
├─────────────────────────────────────────────────────────────┤
│  LOAD                                                       │
│  └── Save to Parquet format                                 │
└─────────────────────────────────────────────────────────────┘

Technical Features Added
Feature	Description	Formula
daily_return	Daily percentage change	(close[t] - close[t-1]) / close[t-1]
MA5	5-day Simple Moving Average	mean(close[t-4:t+1])
MA20	20-day Simple Moving Average	mean(close[t-19:t+1])
Vol_20	20-day Rolling Volatility	std(daily_return[t-19:t+1])

Data Cleaning Strategy
Forward Fill (ffill) + Backward Fill (bfill)

Original:           After ffill:        After bfill:
─────────────────────────────────────────────────────
Row 0: NaN          Row 0: NaN          Row 0: 100  ← bfill
Row 1: 100          Row 1: 100          Row 1: 100
Row 2: NaN    →     Row 2: 100    →     Row 2: 100  ← ffill
Row 3: 105          Row 3: 105          Row 3: 105

Programmatic Usage
import pandas as pd
from src.processors import DataProcessor

# Load raw data
df = pd.read_csv('data/raw/stock_data.csv')

# Create processor and run pipeline
processor = DataProcessor(df)
processor.clean()           # Handle NaN, duplicates
processor.add_features()    # Add MA5, MA20, Vol_20

# Save to Parquet
processor.save_to_parquet('data/processed/output.parquet')

# Or use method chaining
processor = DataProcessor(df)
processor.clean().add_features().save_to_parquet('output.parquet')

Sample Output
============================================================
        🏭 ETL PIPELINE
============================================================

📥 STEP 1: EXTRACT
----------------------------------------
   Reading: data/raw/stock_data_dirty.csv
   ✅ Loaded 25 rows, 6 columns
   Missing values: 4

🧹 STEP 2: TRANSFORM (Cleaning)
----------------------------------------
   ✅ Missing values after cleaning: 0
   ✅ Duplicate dates removed

⚙️  STEP 3: TRANSFORM (Feature Engineering)
----------------------------------------
   ✅ New features added: ['daily_return', 'MA5', 'MA20', 'Vol_20']
   MA5:  21 valid values (first 4 are NaN)
   MA20: 6 valid values (first 19 are NaN)

💾 STEP 4: LOAD
----------------------------------------
✅ Data saved to: data/processed/market_data.parquet
   Rows: 25, Columns: 10

============================================================
✅ ETL Pipeline completed successfully!
============================================================


Important Notes
⚠️ No Look-ahead Bias
All calculations use only past data. The rolling() function includes:

Current row
Previous (N-1) rows

# ✅ Correct: MA5 uses rows [t-4, t-3, t-2, t-1, t]
df['MA5'] = df['close'].rolling(window=5).mean()

# ❌ Wrong: Using future data would cause look-ahead bias
# df['MA5'] = df['close'].shift(-2).rolling(window=5).mean()

NaN Values in Features
Feature	First N rows are NaN	Reason
daily_return	1	No previous day to compare
MA5	4	Need 5 days of data
MA20	19	Need 20 days of data
Vol_20	20	Need 20 returns (21 prices)

🧪 Testing
Run All Tests
pytest tests/ -v

Run Specific Test File
# Test metrics module
pytest tests/test_metrics.py -v

# Test data checker module
pytest tests/test_checker.py -v

# Test data processor module
pytest tests/test_processors.py -v

Test Coverage Summary
Module	Tests	Coverage
metrics.py	14	mean, std, max_drawdown
data_checker.py	18	All quality checks
processors.py	22	Cleaning, features, file I/O
Total	54

📝 Data Formats
Input: OHLCV CSV

date,open,high,low,close,volume
2024-01-01,100.00,105.00,99.00,103.00,1000000
2024-01-02,103.00,108.00,102.00,106.00,1100000

Output: Processed Parquet
Column	Type	Description
date	datetime	Trading date
open	float	Opening price
high	float	Highest price
low	float	Lowest price
close	float	Closing price
volume	int	Trading volume
daily_return	float	Daily return (%)
MA5	float	5-day moving average
MA20	float	20-day moving average
Vol_20	float	20-day volatility

⚠️ Important Notes
Vectorized Operations
All data processing uses Pandas vectorized operations for performance:

# ✅ Correct (fast) - Vectorized
df['MA5'] = df['close'].rolling(window=5).mean()

# ❌ Wrong (slow) - Row iteration
for i in range(len(df)):
    df.loc[i, 'MA5'] = df['close'].iloc[max(0,i-4):i+1].mean()
    
Parquet vs CSV
Aspect	CSV	Parquet
Read Speed	Slow	10-100x faster
File Size	Large	Compressed
Type Preservation	No	Yes
Human Readable	Yes	No

🛠️ Development Log
Version	Task	Description
v0.1	L0-Task1	Project skeleton, metrics, basic report
v0.2	L0-Task2	Data quality checker with tests
v0.3	L1-Task1	ETL pipeline: cleaning & feature engineering


📄 License
MIT License


---

## 5.3 提交到 Git

```bash
git add .
git commit -m "Update README with L1-Task1 ETL pipeline documentation"

5.4 查看 Git 提交历史
git log --oneline
你应该看到多次提交记录。

5.5 最终验收检查
# 1. 运行所有测试
pytest tests/ -v

# 2. 运行 ETL 脚本
python scripts/run_etl.py --verify

# 3. 检查生成的 Parquet 文件
python -c "import pandas as pd; df = pd.read_parquet('data/processed/market_data.parquet'); print(df.head())"


