"""
check_my_data.py - Data Quality Check Script

This script loads a CSV file containing OHLCV data and runs
a comprehensive quality check, outputting a formatted report.

Usage:
    python scripts/check_my_data.py
    python scripts/check_my_data.py path/to/your/data.csv

Author: [Your Name]
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.data_checker import DataQualityChecker


def main():
    """Main function to run data quality check."""
    
    print()
    print("=" * 60)
    print("    🔍 FINANCIAL DATA QUALITY CHECKER")
    print("=" * 60)
    print()
    
    # ===== 1. Determine file path =====
    if len(sys.argv) > 1:
        # User provided a file path as argument
        file_path = sys.argv[1]
    else:
        # Default to the dirty test data
        file_path = "data/raw/dirty_stock_data.csv"
    
    print(f"📂 File: {file_path}")
    print()
    
    # ===== 2. Check if file exists =====
    if not os.path.exists(file_path):
        print(f"❌ Error: File not found: {file_path}")
        print()
        print("Usage:")
        print("    python scripts/check_my_data.py [path/to/file.csv]")
        print()
        print("Example:")
        print("    python scripts/check_my_data.py data/raw/dirty_stock_data.csv")
        return 1
    
    # ===== 3. Load CSV file =====
    print("📊 Loading data...")
    try:
        df = pd.read_csv(file_path)
        print(f"   ✅ Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"   Columns: {list(df.columns)}")
        print()
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return 1
    
    # ===== 4. Run quality check =====
    print("🔍 Running quality checks...")
    print()
    
    try:
        checker = DataQualityChecker(df)
        report = checker.run_all_checks()
        checker.print_report()
    except ValueError as e:
        print(f"❌ Validation Error: {e}")
        print()
        print("Make sure your CSV has these columns:")
        print("   date, open, high, low, close, volume")
        return 1
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return 1
    
    # ===== 5. Return exit code based on issues =====
    total_issues = (
        sum(report['missing_values'].values()) +
        report['duplicate_dates'] +
        report['logical_errors_total'] +
        report['large_gaps'] +
        report['extreme_moves']
    )
    
    if total_issues > 0:
        return 1  # Issues found
    else:
        return 0  # All clean


def show_data_preview(df, rows=5):
    """Show a preview of the data."""
    print("📋 DATA PREVIEW (first 5 rows):")
    print("-" * 60)
    print(df.head(rows).to_string(index=False))
    print("-" * 60)
    print()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
