"""
test_processors.py - Unit tests for DataProcessor

This file contains tests to verify:
- Data cleaning (ffill, bfill, duplicates)
- Feature engineering (MA5, MA20, Vol_20)
- File operations (Parquet save/load)

Run with: pytest tests/test_processors.py -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np
import tempfile

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processors import DataProcessor


# ================================================================
# Helper Function: Create test data
# ================================================================

def create_sample_data(rows=25):
    """Create a clean sample DataFrame for testing."""
    dates = pd.date_range(start='2024-01-01', periods=rows, freq='D')
    
    # Generate price data (upward trend with some noise)
    np.random.seed(42)  # For reproducibility
    close_prices = 100 + np.cumsum(np.random.randn(rows) * 2)
    
    return pd.DataFrame({
        'date': dates,
        'open': close_prices - 1,
        'high': close_prices + 2,
        'low': close_prices - 2,
        'close': close_prices,
        'volume': np.random.randint(1000000, 2000000, rows)
    })


def create_dirty_data():
    """Create a DataFrame with missing values for testing."""
    return pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', 
                 '2024-01-04', '2024-01-05', '2024-01-06'],
        'open':   [100, np.nan, 104, 106, np.nan, 110],
        'high':   [105, 108, 109, 111, 113, 115],
        'low':    [99, 101, 103, 105, 107, 109],
        'close':  [103, 107, np.nan, 109, 111, 113],
        'volume': [1000000, 1100000, 1200000, 1300000, 1400000, 1500000]
    })


# ================================================================
# TEST: Data Cleaning - Missing Values
# ================================================================

def test_ffill_missing_values():
    """Test that middle NaN values are forward-filled."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':  [100, 102, 104],
        'high':  [105, 107, 109],
        'low':   [99, 101, 103],
        'close': [103, np.nan, 107],  # NaN in the middle
        'volume': [1000000, 1100000, 1200000]
    })
    
    processor = DataProcessor(df)
    processor.clean()
    
    # Row 1's close should be filled with Row 0's value (103)
    assert processor.df['close'].iloc[1] == 103, "ffill should use previous value"
    
    # No NaN should remain
    assert processor.df['close'].isna().sum() == 0, "No NaN should remain"


def test_bfill_first_row_nan():
    """Test that NaN in first row is backward-filled."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':  [np.nan, 102, 104],  # NaN at the beginning
        'high':  [105, 107, 109],
        'low':   [99, 101, 103],
        'close': [103, 105, 107],
        'volume': [1000000, 1100000, 1200000]
    })
    
    processor = DataProcessor(df)
    processor.clean()
    
    # Row 0's open should be filled with Row 1's value (102)
    assert processor.df['open'].iloc[0] == 102, "bfill should use next value"
    
    # No NaN should remain
    assert processor.df['open'].isna().sum() == 0, "No NaN should remain"


def test_combined_ffill_bfill():
    """Test that ffill + bfill handles all NaN positions."""
    df = create_dirty_data()
    
    processor = DataProcessor(df)
    processor.clean()
    
    # All NaN should be filled
    total_nan = processor.df.isna().sum().sum()
    assert total_nan == 0, f"Expected 0 NaN, found {total_nan}"


def test_no_nan_after_clean():
    """Test that clean() removes all NaN from numeric columns."""
    df = create_dirty_data()
    
    processor = DataProcessor(df)
    processor.clean()
    
    # Check each column
    for col in ['open', 'high', 'low', 'close', 'volume']:
        nan_count = processor.df[col].isna().sum()
        assert nan_count == 0, f"Column {col} still has {nan_count} NaN values"


# ================================================================
# TEST: Data Cleaning - Duplicates
# ================================================================

def test_remove_duplicate_dates():
    """Test that duplicate dates are removed."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-02', '2024-01-03'],  # Duplicate!
        'open':  [100, 102, 103, 104],
        'high':  [105, 107, 108, 109],
        'low':   [99, 101, 102, 103],
        'close': [103, 105, 106, 107],
        'volume': [1000000, 1100000, 1150000, 1200000]
    })
    
    processor = DataProcessor(df)
    processor.clean()
    
    # Should have 3 rows, not 4
    assert len(processor.df) == 3, f"Expected 3 rows, got {len(processor.df)}"
    
    # No duplicate dates
    assert processor.df['date'].duplicated().sum() == 0, "Duplicates should be removed"


def test_keep_first_duplicate():
    """Test that the first occurrence of duplicate is kept."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-02'],
        'open':  [100, 102, 999],  # 999 should be dropped (duplicate date)
        'high':  [105, 107, 109],
        'low':   [99, 101, 103],
        'close': [103, 105, 107],
        'volume': [1000000, 1100000, 1200000]
    })
    
    processor = DataProcessor(df)
    processor.clean()
    
    # The kept row should have open=102, not 999
    jan2_open = processor.df[processor.df['date'] == '2024-01-02']['open'].iloc[0]
    assert jan2_open == 102, "First occurrence should be kept"


# ================================================================
# TEST: Feature Engineering - Moving Averages
# ================================================================

def test_ma5_calculation():
    """Test that MA5 is calculated correctly."""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=6),
        'open':  [100, 102, 104, 106, 108, 110],
        'high':  [105, 107, 109, 111, 113, 115],
        'low':   [99, 101, 103, 105, 107, 109],
        'close': [100, 102, 104, 106, 108, 110],  # Simple sequence
        'volume': [1000000] * 6
    })
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # MA5 of row 4 (index 4) = (100+102+104+106+108) / 5 = 104
    expected_ma5 = (100 + 102 + 104 + 106 + 108) / 5
    actual_ma5 = processor.df['MA5'].iloc[4]
    
    assert abs(actual_ma5 - expected_ma5) < 0.001, \
        f"Expected MA5={expected_ma5}, got {actual_ma5}"


def test_ma5_first_four_rows_nan():
    """Test that MA5 is NaN for first 4 rows (not enough data)."""
    df = create_sample_data(10)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # First 4 rows should be NaN
    for i in range(4):
        assert pd.isna(processor.df['MA5'].iloc[i]), \
            f"Row {i} MA5 should be NaN"
    
    # Row 4 (5th row) should have a value
    assert pd.notna(processor.df['MA5'].iloc[4]), \
        "Row 4 MA5 should have a value"


def test_ma20_calculation():
    """Test that MA20 is calculated correctly."""
    df = create_sample_data(25)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # First 19 rows should be NaN
    for i in range(19):
        assert pd.isna(processor.df['MA20'].iloc[i]), \
            f"Row {i} MA20 should be NaN"
    
    # Row 19 (20th row) should have a value
    assert pd.notna(processor.df['MA20'].iloc[19]), \
        "Row 19 MA20 should have a value"
    
    # Verify calculation: average of first 20 close prices
    expected_ma20 = df['close'].iloc[:20].mean()
    actual_ma20 = processor.df['MA20'].iloc[19]
    
    assert abs(actual_ma20 - expected_ma20) < 0.001, \
        f"Expected MA20={expected_ma20}, got {actual_ma20}"


def test_ma_no_lookahead_bias():
    """Test that MA calculation doesn't use future data."""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'open':  [100] * 10,
        'high':  [105] * 10,
        'low':   [99] * 10,
        'close': [100, 100, 100, 100, 100, 200, 200, 200, 200, 200],  # Jump at row 5
        'volume': [1000000] * 10
    })
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # MA5 at row 4 should be 100 (only uses rows 0-4, all 100)
    # It should NOT include the 200 from row 5
    assert processor.df['MA5'].iloc[4] == 100, \
        "MA5 should not include future data"


# ================================================================
# TEST: Feature Engineering - Daily Return
# ================================================================

def test_daily_return_calculation():
    """Test that daily return is calculated correctly."""
    df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=3),
        'open':  [100, 102, 104],
        'high':  [105, 107, 109],
        'low':   [99, 101, 103],
        'close': [100, 110, 99],  # +10%, -10%
        'volume': [1000000] * 3
    })
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # Row 0: NaN (no previous day)
    assert pd.isna(processor.df['daily_return'].iloc[0])
    
    # Row 1: (110 - 100) / 100 = 0.10 = 10%
    expected_return_1 = (110 - 100) / 100
    actual_return_1 = processor.df['daily_return'].iloc[1]
    assert abs(actual_return_1 - expected_return_1) < 0.0001
    
    # Row 2: (99 - 110) / 110 = -0.10 = -10%
    expected_return_2 = (99 - 110) / 110
    actual_return_2 = processor.df['daily_return'].iloc[2]
    assert abs(actual_return_2 - expected_return_2) < 0.0001


def test_daily_return_first_row_nan():
    """Test that first row's daily return is NaN."""
    df = create_sample_data(5)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    assert pd.isna(processor.df['daily_return'].iloc[0]), \
        "First row's daily return should be NaN"


# ================================================================
# TEST: Feature Engineering - Volatility
# ================================================================

def test_vol20_exists():
    """Test that Vol_20 column is created."""
    df = create_sample_data(25)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    assert 'Vol_20' in processor.df.columns, "Vol_20 column should exist"


def test_vol20_first_rows_nan():
    """Test that Vol_20 is NaN for insufficient data."""
    df = create_sample_data(25)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # First 20 rows should be NaN (need 20 returns, but first return is NaN)
    for i in range(20):
        assert pd.isna(processor.df['Vol_20'].iloc[i]), \
            f"Row {i} Vol_20 should be NaN"


def test_vol20_has_values():
    """Test that Vol_20 has values after enough data."""
    df = create_sample_data(25)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # Row 20 onwards should have values
    assert pd.notna(processor.df['Vol_20'].iloc[20]), \
        "Row 20 Vol_20 should have a value"


# ================================================================
# TEST: File Operations
# ================================================================

def test_save_to_parquet():
    """Test that data can be saved to Parquet format."""
    df = create_sample_data(10)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # Use temporary file
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
        temp_path = f.name
    
    try:
        processor.save_to_parquet(temp_path)
        
        # Verify file exists
        assert os.path.exists(temp_path), "Parquet file should be created"
        
        # Verify file can be read
        df_loaded = pd.read_parquet(temp_path)
        assert len(df_loaded) == len(processor.df), "Row count should match"
        
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_parquet_preserves_data():
    """Test that Parquet preserves data correctly."""
    df = create_sample_data(10)
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    with tempfile.NamedTemporaryFile(suffix='.parquet', delete=False) as f:
        temp_path = f.name
    
    try:
        processor.save_to_parquet(temp_path)
        df_loaded = pd.read_parquet(temp_path)
        
        # Check columns match
        assert list(df_loaded.columns) == list(processor.df.columns), \
            "Columns should match"
        
        # Check close prices match
        assert list(df_loaded['close']) == list(processor.df['close']), \
            "Close prices should match"
        
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ================================================================
# TEST: Method Chaining
# ================================================================

def test_method_chaining():
    """Test that methods can be chained."""
    df = create_dirty_data()
    
    # This should work without errors
    processor = DataProcessor(df)
    result = processor.clean().add_features()
    
    # Result should be the processor itself
    assert result is processor, "Methods should return self for chaining"
    
    # Features should be added
    assert 'MA5' in processor.df.columns, "MA5 should exist after chaining"


# ================================================================
# TEST: Edge Cases
# ================================================================

def test_already_clean_data():
    """Test that clean data is not corrupted."""
    df = create_sample_data(10)
    original_close = df['close'].tolist()
    
    processor = DataProcessor(df)
    processor.clean()
    
    # Close prices should be unchanged
    assert processor.df['close'].tolist() == original_close, \
        "Clean data should not be modified"


def test_get_dataframe_returns_copy():
    """Test that get_dataframe returns a copy, not the original."""
    df = create_sample_data(5)
    
    processor = DataProcessor(df)
    processor.clean()
    
    df_copy = processor.get_dataframe()
    df_copy['close'] = 999  # Modify the copy
    
    # Original should be unchanged
    assert processor.df['close'].iloc[0] != 999, \
        "get_dataframe should return a copy"


def test_original_df_not_modified():
    """Test that the original DataFrame is not modified."""
    df = create_dirty_data()
    original_nan_count = df.isna().sum().sum()
    
    processor = DataProcessor(df)
    processor.clean()
    processor.add_features()
    
    # Original df should still have NaN
    current_nan_count = df.isna().sum().sum()
    assert current_nan_count == original_nan_count, \
        "Original DataFrame should not be modified"


# ================================================================
# Run tests directly (optional)
# ================================================================

if __name__ == "__main__":
    print("Please run tests with: pytest tests/test_processors.py -v")
