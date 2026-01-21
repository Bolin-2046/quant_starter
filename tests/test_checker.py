"""
test_checker.py - Unit tests for DataQualityChecker

This file contains tests to verify that the data quality checker
correctly identifies various data issues.

Run with: pytest tests/test_checker.py -v
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_checker import DataQualityChecker


# ================================================================
# Helper Function: Create clean base data
# ================================================================

def create_clean_data():
    """Create a clean DataFrame with no issues."""
    return pd.DataFrame({
        'date': [
            '2024-01-01', '2024-01-02', '2024-01-03',
            '2024-01-04', '2024-01-05'
        ],
        'open':   [100, 102, 104, 106, 108],
        'high':   [105, 107, 109, 111, 113],
        'low':    [99,  101, 103, 105, 107],
        'close':  [103, 105, 107, 109, 111],
        'volume': [1000, 1100, 1200, 1300, 1400]
    })


# ================================================================
# TEST 1: Missing Values (空值检测)
# ================================================================

def test_missing_values_detected():
    """Test that missing values (NaN) are correctly detected."""
    # Create data with missing values
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':   [100, 102, np.nan],       # 1 missing
        'high':   [105, 107, 109],
        'low':    [99,  101, 103],
        'close':  [103, np.nan, np.nan],    # 2 missing
        'volume': [1000, 1100, 1200]
    })
    
    checker = DataQualityChecker(df)
    missing = checker.check_missing_values()
    
    # Verify results
    assert 'open' in missing, "Should detect missing 'open'"
    assert missing['open'] == 1, "Should find 1 missing 'open'"
    assert 'close' in missing, "Should detect missing 'close'"
    assert missing['close'] == 2, "Should find 2 missing 'close'"


def test_no_missing_values():
    """Test that clean data reports no missing values."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    missing = checker.check_missing_values()
    
    assert missing == {}, "Clean data should have no missing values"


# ================================================================
# TEST 2: Duplicate Dates (重复日期检测)
# ================================================================

def test_duplicate_dates_detected():
    """Test that duplicate dates are correctly detected."""
    df = pd.DataFrame({
        'date': [
            '2024-01-01', 
            '2024-01-02', 
            '2024-01-02',   # Duplicate!
            '2024-01-03'
        ],
        'open':   [100, 102, 103, 104],
        'high':   [105, 107, 108, 109],
        'low':    [99,  101, 102, 103],
        'close':  [103, 105, 106, 107],
        'volume': [1000, 1100, 1150, 1200]
    })
    
    checker = DataQualityChecker(df)
    duplicates = checker.check_duplicate_dates()
    
    assert duplicates == 1, f"Should find 1 duplicate, found {duplicates}"


def test_no_duplicate_dates():
    """Test that clean data has no duplicate dates."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    duplicates = checker.check_duplicate_dates()
    
    assert duplicates == 0, "Clean data should have no duplicates"


# ================================================================
# TEST 3: High < Low Error (逻辑矛盾检测)
# ================================================================

def test_high_low_error_detected():
    """Test that high < low inconsistency is detected."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':   [100, 102, 104],
        'high':   [105, 100, 109],   # Row 2: high=100
        'low':    [99,  110, 103],   # Row 2: low=110  --> high < low!
        'close':  [103, 105, 107],
        'volume': [1000, 1100, 1200]
    })
    
    checker = DataQualityChecker(df)
    errors = checker.check_high_low_consistency()
    
    assert errors == 1, f"Should find 1 high<low error, found {errors}"


def test_no_high_low_errors():
    """Test that clean data has no high<low errors."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    errors = checker.check_high_low_consistency()
    
    assert errors == 0, "Clean data should have no high<low errors"


# ================================================================
# TEST 4: Price Out of Range (价格越界检测)
# ================================================================

def test_price_out_of_range_detected():
    """Test that open/close outside [low, high] is detected."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':   [100, 120, 104],   # Row 2: open=120 > high=107!
        'high':   [105, 107, 109],
        'low':    [99,  101, 103],
        'close':  [103, 105, 95],    # Row 3: close=95 < low=103!
        'volume': [1000, 1100, 1200]
    })
    
    checker = DataQualityChecker(df)
    errors = checker.check_price_range()
    
    assert errors == 2, f"Should find 2 out-of-range errors, found {errors}"


def test_no_price_range_errors():
    """Test that clean data has no price range errors."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    errors = checker.check_price_range()
    
    assert errors == 0, "Clean data should have no price range errors"


# ================================================================
# TEST 5: Negative Values (负数检测)
# ================================================================

def test_negative_values_detected():
    """Test that negative prices/volume are detected."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':   [-100, 102, 104],    # Row 1: negative open
        'high':   [105, 107, 109],
        'low':    [99,  101, 103],
        'close':  [103, 105, 107],
        'volume': [1000, -500, 1200]   # Row 2: negative volume
    })
    
    checker = DataQualityChecker(df)
    negatives = checker.check_negative_values()
    
    assert negatives == 2, f"Should find 2 negative value rows, found {negatives}"


def test_no_negative_values():
    """Test that clean data has no negative values."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    negatives = checker.check_negative_values()
    
    assert negatives == 0, "Clean data should have no negative values"


# ================================================================
# TEST 6: Date Gaps (日期断档检测)
# ================================================================

def test_date_gaps_detected():
    """Test that large date gaps (>3 days) are detected."""
    df = pd.DataFrame({
        'date': [
            '2024-01-01',
            '2024-01-02',
            '2024-01-10',   # Gap of 8 days!
            '2024-01-11'
        ],
        'open':   [100, 102, 104, 106],
        'high':   [105, 107, 109, 111],
        'low':    [99,  101, 103, 105],
        'close':  [103, 105, 107, 109],
        'volume': [1000, 1100, 1200, 1300]
    })
    
    checker = DataQualityChecker(df)
    gap_info = checker.check_date_gaps()
    
    assert gap_info['large_gaps'] == 1, "Should find 1 large gap"
    assert gap_info['max_gap_days'] == 8, "Max gap should be 8 days"


def test_no_large_date_gaps():
    """Test that consecutive dates have no large gaps."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    gap_info = checker.check_date_gaps()
    
    assert gap_info['large_gaps'] == 0, "Should have no large gaps"
    assert gap_info['max_gap_days'] == 1, "Max gap should be 1 day"


# ================================================================
# TEST 7: Extreme Moves (异常波动检测)
# ================================================================

def test_extreme_moves_detected():
    """Test that extreme price moves (>10%) are detected."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04'],
        'open':   [100, 102, 104, 106],
        'high':   [105, 125, 109, 111],
        'low':    [99,  101, 90,  105],
        'close':  [100, 115, 92, 109],  # Day 2: +15%, Day 3: -20%
        'volume': [1000, 1100, 1200, 1300]
    })
    
    checker = DataQualityChecker(df)
    extreme = checker.check_extreme_moves()
    
    assert extreme == 3, f"Should find 2 extreme moves, found {extreme}"


def test_no_extreme_moves():
    """Test that stable prices have no extreme moves."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'open':   [100, 101, 102],
        'high':   [102, 103, 104],
        'low':    [99,  100, 101],
        'close':  [101, 102, 103],   # +1% each day, very stable
        'volume': [1000, 1100, 1200]
    })
    
    checker = DataQualityChecker(df)
    extreme = checker.check_extreme_moves()
    
    assert extreme == 0, "Stable data should have no extreme moves"


# ================================================================
# TEST 8: Full Report (完整报告测试)
# ================================================================

def test_run_all_checks():
    """Test that run_all_checks returns a complete report."""
    df = create_clean_data()
    
    checker = DataQualityChecker(df)
    report = checker.run_all_checks()
    
    # Check all expected keys exist
    expected_keys = [
        'total_rows',
        'missing_values',
        'duplicate_dates',
        'high_low_errors',
        'price_range_errors',
        'negative_values',
        'logical_errors_total',
        'large_gaps',
        'max_gap_days',
        'extreme_moves'
    ]
    
    for key in expected_keys:
        assert key in report, f"Report should contain '{key}'"
    
    # Clean data should have no issues
    assert report['total_rows'] == 5
    assert report['duplicate_dates'] == 0
    assert report['logical_errors_total'] == 0


# ================================================================
# TEST 9: Column Validation (列验证测试)
# ================================================================

def test_missing_columns_raises_error():
    """Test that missing required columns raise an error."""
    # DataFrame missing 'volume' column
    df = pd.DataFrame({
        'date': ['2024-01-01'],
        'open':   [100],
        'high':   [105],
        'low':    [99],
        'close':  [103]
        # Missing 'volume'!
    })
    
    # Should raise ValueError
    with pytest.raises(ValueError) as excinfo:
        checker = DataQualityChecker(df)
    
    assert "volume" in str(excinfo.value).lower()


# ================================================================
# TEST 10: Edge Cases (边界情况)
# ================================================================

def test_single_row_data():
    """Test that checker handles single row data."""
    df = pd.DataFrame({
        'date': ['2024-01-01'],
        'open':   [100],
        'high':   [105],
        'low':    [99],
        'close':  [103],
        'volume': [1000]
    })
    
    checker = DataQualityChecker(df)
    report = checker.run_all_checks()
    
    assert report['total_rows'] == 1
    assert report['extreme_moves'] == 0  # No previous day to compare


def test_all_same_prices():
    """Test data where all OHLC are the same (limit up/down)."""
    df = pd.DataFrame({
        'date': ['2024-01-01', '2024-01-02'],
        'open':   [100, 100],
        'high':   [100, 100],  # All same
        'low':    [100, 100],  # All same
        'close':  [100, 100],
        'volume': [1000, 1000]
    })
    
    checker = DataQualityChecker(df)
    report = checker.run_all_checks()
    
    # This is valid data (e.g., stock at limit)
    assert report['high_low_errors'] == 0
    assert report['price_range_errors'] == 0


# ================================================================
# Run tests directly (optional)
# ================================================================

if __name__ == "__main__":
    print("Please run tests with: pytest tests/test_checker.py -v")
