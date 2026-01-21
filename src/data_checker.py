"""
data_checker.py - Financial Data Quality Inspector

This module provides tools to check OHLCV data for common issues:
- Missing values (NaN)
- Duplicate dates
- Logical inconsistencies (high < low, etc.)
- Date gaps
- Extreme price movements

Author: [Your Name]
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


class DataQualityChecker:
    """
    A class to perform quality checks on OHLCV financial data.
    
    OHLCV = Open, High, Low, Close, Volume
    
    Usage:
        checker = DataQualityChecker(df)
        report = checker.run_all_checks()
    """
    
    # Required columns for OHLCV data
    REQUIRED_COLUMNS = ['date', 'open', 'high', 'low', 'close', 'volume']
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the checker with a DataFrame.
        
        Args:
            df: DataFrame containing OHLCV data
            
        Raises:
            ValueError: If required columns are missing
        """
        # Make a copy to avoid modifying the original data
        self.df = df.copy()
        
        # Validate required columns exist
        self._validate_columns()
        
        # Convert date column to datetime
        self._prepare_date_column()
        
        # Initialize report dictionary
        self.report = {}
    
    def _validate_columns(self):
        """Check if all required columns exist in the DataFrame."""
        missing_cols = []
        for col in self.REQUIRED_COLUMNS:
            if col not in self.df.columns:
                missing_cols.append(col)
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    def _prepare_date_column(self):
        """Convert date column to datetime format."""
        self.df['date'] = pd.to_datetime(self.df['date'])
    
    # ================================================================
    # CHECK 1: Basic Integrity (基础完整性)
    # ================================================================
    
    def check_missing_values(self) -> Dict[str, int]:
        """
        Check for missing values (NaN) in each column.
        
        Returns:
            Dict mapping column names to count of missing values
        """
        # Use isnull() to find NaN, sum() to count them
        missing = self.df.isnull().sum()
        
        # Convert to dictionary, only include columns with missing values
        missing_dict = missing[missing > 0].to_dict()
        
        return missing_dict
    
    def check_duplicate_dates(self) -> int:
        """
        Check for duplicate dates.
        
        Returns:
            Number of duplicate date entries
        """
        # duplicated() returns True for duplicate rows
        # keep='first' means first occurrence is not marked as duplicate
        duplicate_count = self.df['date'].duplicated(keep='first').sum()
        
        return int(duplicate_count)
    
    # ================================================================
    # CHECK 2: Logical Consistency (逻辑一致性)
    # ================================================================
    
    def check_high_low_consistency(self) -> int:
        """
        Check if high < low (which is impossible).
        
        Returns:
            Number of rows where high < low
        """
        # Vectorized comparison: compare entire columns at once
        invalid_rows = self.df['high'] < self.df['low']
        
        return int(invalid_rows.sum())
    
    def check_price_range(self) -> int:
        """
        Check if open and close are within [low, high] range.
        
        Returns:
            Number of rows where open or close is out of range
        """
        # Check if open is within range
        open_below_low = self.df['open'] < self.df['low']
        open_above_high = self.df['open'] > self.df['high']
        
        # Check if close is within range
        close_below_low = self.df['close'] < self.df['low']
        close_above_high = self.df['close'] > self.df['high']
        
        # Combine all conditions with OR (|)
        out_of_range = open_below_low | open_above_high | close_below_low | close_above_high
        
        return int(out_of_range.sum())
    
    def check_negative_values(self) -> int:
        """
        Check for negative prices or volume.
        
        Returns:
            Number of rows with negative values
        """
        price_cols = ['open', 'high', 'low', 'close', 'volume']
        
        # Check each column for negative values
        negative_mask = pd.Series([False] * len(self.df))
        
        for col in price_cols:
            # Use | to combine: any column being negative marks the row
            negative_mask = negative_mask | (self.df[col] < 0)
        
        return int(negative_mask.sum())
    
    def get_total_logical_errors(self) -> int:
        """
        Get total count of rows with any logical error.
        
        Returns:
            Total number of rows with logical errors
        """
        # High < Low
        hl_error = self.df['high'] < self.df['low']
        
        # Open/Close out of range
        open_error = (self.df['open'] < self.df['low']) | (self.df['open'] > self.df['high'])
        close_error = (self.df['close'] < self.df['low']) | (self.df['close'] > self.df['high'])
        
        # Negative values
        neg_error = (
            (self.df['open'] < 0) | 
            (self.df['high'] < 0) | 
            (self.df['low'] < 0) | 
            (self.df['close'] < 0) | 
            (self.df['volume'] < 0)
        )
        
        # Combine all errors
        any_error = hl_error | open_error | close_error | neg_error
        
        return int(any_error.sum())
    
    # ================================================================
    # CHECK 3: Continuity (连续性检查)
    # ================================================================
    
    def check_date_gaps(self) -> Dict[str, Any]:
        """
        Check for gaps in dates (missing trading days).
        
        Returns:
            Dict with:
                - large_gaps: count of gaps > 3 days
                - max_gap_days: maximum gap in days
        """
        # Sort by date first
        sorted_df = self.df.sort_values('date')
        
        # Calculate difference between consecutive dates
        # diff() calculates the difference between current and previous row
        date_diffs = sorted_df['date'].diff()
        
        # Convert to days (timedelta to integer)
        # dropna() removes the first row (which has no previous date)
        gap_days = date_diffs.dt.days.dropna()
        
        # Count gaps larger than 3 days
        large_gaps = (gap_days > 3).sum()
        
        # Find maximum gap
        max_gap = int(gap_days.max()) if len(gap_days) > 0 else 0
        
        return {
            'large_gaps': int(large_gaps),
            'max_gap_days': max_gap
        }
    
    # ================================================================
    # CHECK 4: Outliers / Extreme Moves (异常波动)
    # ================================================================
    
    def check_extreme_moves(self, threshold: float = 0.10) -> int:
        """
        Check for extreme daily price movements.
        
        Args:
            threshold: Maximum allowed daily change (default 10%)
            
        Returns:
            Number of days with moves exceeding threshold
        """
        # Sort by date to ensure correct order
        sorted_df = self.df.sort_values('date').copy()
        
        # Get previous day's close price using shift()
        # shift(1) moves all values down by 1 row
        prev_close = sorted_df['close'].shift(1)
        
        # Calculate daily return: (today - yesterday) / yesterday
        # Use np.where to handle division by zero
        daily_return = np.where(
            prev_close != 0,                          # Condition
            (sorted_df['close'] - prev_close) / prev_close,  # If True
            np.nan                                    # If False (avoid div by zero)
        )
        
        # Count absolute returns exceeding threshold
        extreme_count = (np.abs(daily_return) > threshold).sum()
        
        # Subtract NaN count (first row has no return)
        extreme_count = int(extreme_count)
        
        return extreme_count
    
    # ================================================================
    # MAIN: Run All Checks
    # ================================================================
    
    def run_all_checks(self) -> Dict[str, Any]:
        """
        Run all quality checks and generate a report.
        
        Returns:
            Dictionary containing all check results
        """
        # Get date gap info
        gap_info = self.check_date_gaps()
        
        # Build the report
        self.report = {
            'total_rows': len(self.df),
            'missing_values': self.check_missing_values(),
            'duplicate_dates': self.check_duplicate_dates(),
            'high_low_errors': self.check_high_low_consistency(),
            'price_range_errors': self.check_price_range(),
            'negative_values': self.check_negative_values(),
            'logical_errors_total': self.get_total_logical_errors(),
            'large_gaps': gap_info['large_gaps'],
            'max_gap_days': gap_info['max_gap_days'],
            'extreme_moves': self.check_extreme_moves()
        }
        
        return self.report
    
    def print_report(self):
        """Print a formatted quality report to console."""
        
        # Run checks if not already done
        if not self.report:
            self.run_all_checks()
        
        # Print formatted report
        print("=" * 60)
        print("        📋 DATA QUALITY REPORT")
        print("=" * 60)
        print()
        
        # Basic Info
        print("📊 BASIC INFO")
        print("-" * 40)
        print(f"   Total Rows: {self.report['total_rows']}")
        print()
        
        # Missing Values
        print("🔍 MISSING VALUES")
        print("-" * 40)
        if self.report['missing_values']:
            for col, count in self.report['missing_values'].items():
                print(f"   {col}: {count} missing")
        else:
            print("   ✅ No missing values")
        print()
        
        # Duplicate Dates
        print("📅 DUPLICATE DATES")
        print("-" * 40)
        if self.report['duplicate_dates'] > 0:
            print(f"   ❌ {self.report['duplicate_dates']} duplicate date(s) found")
        else:
            print("   ✅ No duplicate dates")
        print()
        
        # Logical Errors
        print("⚠️  LOGICAL CONSISTENCY")
        print("-" * 40)
        print(f"   High < Low errors:     {self.report['high_low_errors']}")
        print(f"   Price out of range:    {self.report['price_range_errors']}")
        print(f"   Negative values:       {self.report['negative_values']}")
        print(f"   Total logical errors:  {self.report['logical_errors_total']}")
        print()
        
        # Date Gaps
        print("📆 DATE CONTINUITY")
        print("-" * 40)
        print(f"   Gaps > 3 days:   {self.report['large_gaps']}")
        print(f"   Max gap (days):  {self.report['max_gap_days']}")
        print()
        
        # Extreme Moves
        print("📈 EXTREME PRICE MOVES (>10%)")
        print("-" * 40)
        print(f"   Count: {self.report['extreme_moves']} day(s)")
        print()
        
        # Summary
        print("=" * 60)
        total_issues = (
            sum(self.report['missing_values'].values()) +
            self.report['duplicate_dates'] +
            self.report['logical_errors_total'] +
            self.report['large_gaps'] +
            self.report['extreme_moves']
        )
        
        if total_issues == 0:
            print("✅ RESULT: Data is CLEAN!")
        else:
            print(f"❌ RESULT: {total_issues} issue(s) found. Please review.")
        print("=" * 60)


# ================================================================
# Convenience Function (方便调用的函数)
# ================================================================

def check_data_quality(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to check data quality.
    
    Args:
        df: DataFrame with OHLCV data
        
    Returns:
        Quality report dictionary
    """
    checker = DataQualityChecker(df)
    report = checker.run_all_checks()
    checker.print_report()
    return report
