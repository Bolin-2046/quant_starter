# Quant Starter 📊

A lightweight, standardized Python project skeleton designed for quantitative finance analysis.
This project establishes a foundational structure for data processing, metric calculation (Mean, Volatility, Max Drawdown), and automated performance reporting.

## 📁 Project Structure

```text
quant_starter/
├── README.md               # Project documentation
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
├── data/
│   ├── raw/               # Raw data (e.g., sample_prices.csv)
│   └── processed/         # Processed data
├── src/
│   ├── __init__.py
│   ├── config.py          # Configuration settings
│   ├── io_utils.py        # I/O utilities (CSV handling)
│   └── metrics.py         # Core metric calculations
├── tests/
│   ├── __init__.py
│   └── test_metrics.py    # Unit tests
└── scripts/
    └── run_basic_report.py  # Entry point script
    
🚀 Getting Started

1. Prerequisites
Ensure you have Python 3.8+ installed on your system.

2. Installation
Clone the repository and install the required dependencies:

pip install -r requirements.txt

3. Usage
Run the main analysis script to process the sample data and generate a performance report:

python scripts/run_basic_report.py

Expected Output:

==================================================
        📊 Basic Quantitative Analysis Report
==================================================

📂 Loading Data: data/raw/sample_prices.csv
   Total records: 10

📈 Data Preview:
   Start Date: 2024-01-01, Price: 100.0
   End Date:   2024-01-10, Price: 112.0

📊 Return Statistics:
   Trading Days: 9
   Avg Daily Return: 1.2877%
   Volatility:       2.2067%

💰 NAV Analysis:
   Start NAV:    1.0000
   Final NAV:    1.1200
   Total Return: 12.00%
   Max Drawdown: 4.55%
   
4. Testing
This project includes a suite of unit tests to ensure calculation accuracy. Run the tests using pytest:

pytest tests/test_metrics.py -v

If everything is correct, you should see all tests marked as PASSED.

🧠 Core Metrics Explained
The core logic is located in src/metrics.py:

1. Mean
Calculates the arithmetic average of the dataset.

2. Standard Deviation (Volatility)
Measures the dispersion of a dataset relative to its mean.

Note: This implementation uses Population Standard Deviation (dividing by n), not Sample Standard Deviation (n-1).

3. Max Drawdown
A key risk indicator measuring the largest single drop from peak to bottom in the value of a portfolio (before a new peak is achieved).

Formula: MaxDD = (Peak - Trough) / Peak
Logic:
Iterate through the Net Asset Value (NAV) series.
Track the running maximum (Peak).
Calculate the drawdown for every point relative to that Peak.
Record the maximum drawdown observed.
🛠 Development Log
L0-Task1: Project initialization, CSV I/O implementation, core metric algorithms, and unit testing.

📄 License

MIT License


---

### 📝 How to update your code for English Output

Since you are making this international, you should also update your `scripts/run_basic_report.py` to print English text instead of Chinese.

**Open `scripts/run_basic_report.py` and replace the `main()` function with this:**

```python
def main():
    """Main function: Execute the full analysis process"""
    
    print("=" * 50)
    print("        📊 Basic Quantitative Analysis Report")
    print("=" * 50)
    print()
    
    # ===== 1. Load Data =====
    data_path = "data/raw/sample_prices.csv"
    print(f"📂 Loading Data: {data_path}")
    
    try:
        df = read_csv(data_path)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return
    
    print(f"   Total records: {len(df)}")
    print()
    
    # ===== 2. Extract Prices =====
    prices = df['close'].tolist()
    dates = df['date'].tolist()
    
    print("📈 Data Preview:")
    print(f"   Start Date: {dates[0]}, Price: {prices[0]}")
    print(f"   End Date:   {dates[-1]}, Price: {prices[-1]}")
    print()
    
    # ===== 3. Calculate Returns =====
    returns = calculate_returns(prices)
    print("📊 Return Statistics:")
    print(f"   Trading Days: {len(returns)}")
    print(f"   Avg Daily Return: {mean(returns) * 100:.4f}%")
    print(f"   Volatility:       {std(returns) * 100:.4f}%")
    print()
    
    # ===== 4. Calculate NAV and Max Drawdown =====
    nav = calculate_nav(returns)
    mdd = max_drawdown(nav)
    
    print("💰 NAV Analysis:")
    print(f"   Start NAV:    {nav[0]:.4f}")
    print(f"   Final NAV:    {nav[-1]:.4f}")
    print(f"   Total Return: {(nav[-1] - 1) * 100:.2f}%")
    print(f"   Max Drawdown: {mdd * 100:.2f}%")
    print()
