"""
processors.py - Data Cleaning and Feature Engineering Module

This module provides tools for:
- Cleaning raw OHLCV data (handling NaN, duplicates)
- Adding technical indicators (MA5, MA20, Volatility)
- Saving processed data in efficient formats (Parquet)

Author: [Your Name]
"""

import pandas as pd
import numpy as np
from typing import Optional


class DataProcessor:
    """
    A class to clean financial data and generate technical features.
    
    Workflow:
        1. Initialize with raw DataFrame
        2. Call clean() to handle missing values and duplicates
        3. Call add_features() to compute technical indicators
        4. Call save_to_parquet() to export processed data
    
    Example:
        processor = DataProcessor(df)
        processor.clean()
        processor.add_features()
        processor.save_to_parquet('output.parquet')
    """
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize the processor with a DataFrame.
        
        Args:
            df: Raw DataFrame containing OHLCV data
            
        Note:
            A copy is made to avoid modifying the original data.
        """
        # Make a copy to avoid modifying original data
        self.df = df.copy()
        
        # Convert date column to datetime if it exists
        if 'date' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['date'])
    
    # ================================================================
    # CLEANING METHODS
    # ================================================================
    
    def clean(self) -> 'DataProcessor':
        """
        Clean the data by handling missing values and duplicates.
        
        Steps:
            1. Forward fill (ffill): Use previous day's value
            2. Backward fill (bfill): For NaN at the beginning
            3. Remove duplicate dates
        
        Returns:
            self: For method chaining
            
        Example:
            processor.clean().add_features()
        """
        # Step 1: Handle missing values
        self._fill_missing_values()
        
        # Step 2: Remove duplicate dates
        self._remove_duplicates()
        
        # Step 3: Sort by date
        self._sort_by_date()
        
        return self  # Enable method chaining
    
    def _fill_missing_values(self):
        """
        Fill missing values using forward fill, then backward fill.
        
        Why this order?
            - ffill: If today's data is missing, use yesterday's
            - bfill: If the first row is missing, use the next available
        """
        # Forward fill: propagate last valid value forward
        self.df = self.df.ffill()
        
        # Backward fill: fill remaining NaN at the beginning
        self.df = self.df.bfill()
    
    def _remove_duplicates(self):
        """
        Remove duplicate dates, keeping the first occurrence.
        """
        if 'date' in self.df.columns:
            # Keep first occurrence of each date
            self.df = self.df.drop_duplicates(subset='date', keep='first')
    
    def _sort_by_date(self):
        """
        Sort DataFrame by date in ascending order.
        """
        if 'date' in self.df.columns:
            self.df = self.df.sort_values('date').reset_index(drop=True)
    
    # ================================================================
    # FEATURE ENGINEERING METHODS
    # ================================================================
    
    def add_features(self) -> 'DataProcessor':
        """
        Add technical indicators to the DataFrame.
        
        Features added:
            - daily_return: Daily percentage change
            - MA5: 5-day Simple Moving Average
            - MA20: 20-day Simple Moving Average
            - Vol_20: 20-day rolling volatility (std of returns)
        
        Returns:
            self: For method chaining
            
        Note:
            All calculations use vectorized operations (no for loops).
            No look-ahead bias: only past data is used.
        """
        # Step 1: Calculate daily return
        self._add_daily_return()
        
        # Step 2: Add moving averages
        self._add_moving_averages()
        
        # Step 3: Add volatility
        self._add_volatility()
        
        return self  # Enable method chaining
    
    def _add_daily_return(self):
        """
        Calculate daily return: (today - yesterday) / yesterday
        
        Uses pct_change() which is equivalent to:
            (close[t] - close[t-1]) / close[t-1]
        """
        # pct_change() calculates percentage change from previous row
        # This is safe: no look-ahead bias (only looks at past)
        self.df['daily_return'] = self.df['close'].pct_change()
    
    def _add_moving_averages(self):
        """
        Calculate Simple Moving Averages (SMA).
        
        MA5:  Average of last 5 days' close prices
        MA20: Average of last 20 days' close prices
        
        Note:
            - First 4 rows of MA5 will be NaN (not enough data)
            - First 19 rows of MA20 will be NaN
            - This is correct behavior, NOT an error!
        """
        # 5-day moving average
        # rolling(window=5) looks at current row + 4 previous rows
        self.df['MA5'] = self.df['close'].rolling(window=5).mean()
        
        # 20-day moving average
        self.df['MA20'] = self.df['close'].rolling(window=20).mean()
    
    def _add_volatility(self):
        """
        Calculate 20-day rolling volatility.
        
        Volatility = Standard deviation of daily returns over 20 days
        
        High volatility = prices are jumping around a lot
        Low volatility = prices are relatively stable
        """
        # Calculate std of daily returns over 20-day window
        self.df['Vol_20'] = self.df['daily_return'].rolling(window=20).std()
    
    # ================================================================
    # STORAGE METHODS
    # ================================================================
    
    def save_to_parquet(self, path: str) -> None:
        """
        Save the processed DataFrame to a Parquet file.
        
        Args:
            path: Output file path (e.g., 'data/processed/output.parquet')
            
        Why Parquet?
            - 10-100x faster than CSV for large files
            - Compressed: smaller file size
            - Preserves data types (dates, floats, etc.)
        """
        self.df.to_parquet(path, index=False)
        print(f"✅ Data saved to: {path}")
        print(f"   Rows: {len(self.df)}, Columns: {len(self.df.columns)}")
    
    def save_to_csv(self, path: str) -> None:
        """
        Save the processed DataFrame to a CSV file.
        
        Args:
            path: Output file path
        """
        self.df.to_csv(path, index=False)
        print(f"✅ Data saved to: {path}")
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def get_dataframe(self) -> pd.DataFrame:
        """
        Get the processed DataFrame.
        
        Returns:
            The processed DataFrame
        """
        return self.df.copy()
    
    def summary(self) -> None:
        """
        Print a summary of the processed data.
        """
        print("=" * 50)
        print("        📊 DATA SUMMARY")
        print("=" * 50)
        print(f"\n📋 Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        print(f"\n📅 Date Range:")
        
        if 'date' in self.df.columns:
            print(f"   Start: {self.df['date'].min()}")
            print(f"   End:   {self.df['date'].max()}")
        
        print(f"\n📈 Columns: {list(self.df.columns)}")
        
        print(f"\n🔍 Missing Values:")
        missing = self.df.isnull().sum()
        if missing.sum() == 0:
            print("   ✅ No missing values")
        else:
            for col, count in missing[missing > 0].items():
                print(f"   {col}: {count}")
        
        print(f"\n📊 Sample Data (first 5 rows):")
        print(self.df.head().to_string())
        print("=" * 50)


# ================================================================
# CONVENIENCE FUNCTION
# ================================================================

def process_stock_data(
    input_path: str,
    output_path: str,
    save_format: str = 'parquet'
) -> pd.DataFrame:
    """
    Convenience function to run the full ETL pipeline.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path for output file
        save_format: 'parquet' or 'csv'
        
    Returns:
        Processed DataFrame
        
    Example:
        df = process_stock_data(
            'data/raw/stock.csv',
            'data/processed/stock.parquet'
        )
    """
    # Read raw data
    print(f"📂 Reading: {input_path}")
    df = pd.read_csv(input_path)
    
    # Process
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # Save
    if save_format == 'parquet':
        processor.save_to_parquet(output_path)
    else:
        processor.save_to_csv(output_path)
    
    return processor.get_dataframe()
