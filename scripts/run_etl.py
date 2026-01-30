"""
run_etl.py - ETL Pipeline Runner

This script runs the complete ETL (Extract-Transform-Load) pipeline:
1. Extract: Read raw CSV data
2. Transform: Clean data and add technical features
3. Load: Save processed data to Parquet format

Usage:
    python scripts/run_etl.py
    python scripts/run_etl.py --input path/to/input.csv --output path/to/output.parquet

Author: [Your Name]
"""

import sys
import os
import argparse

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.processors import DataProcessor


def run_etl_pipeline(input_path: str, output_path: str) -> pd.DataFrame:
    """
    Run the complete ETL pipeline.
    
    Args:
        input_path: Path to input CSV file
        output_path: Path for output Parquet file
        
    Returns:
        Processed DataFrame
    """
    
    print()
    print("=" * 60)
    print("        🏭 ETL PIPELINE")
    print("=" * 60)
    print()
    
    # ===== STEP 1: EXTRACT =====
    print("📥 STEP 1: EXTRACT")
    print("-" * 40)
    print(f"   Reading: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"   ❌ Error: File not found: {input_path}")
        return None
    
    try:
        df_raw = pd.read_csv(input_path)
        print(f"   ✅ Loaded {len(df_raw)} rows, {len(df_raw.columns)} columns")
        print(f"   Columns: {list(df_raw.columns)}")
    except Exception as e:
        print(f"   ❌ Error reading file: {e}")
        return None
    
    # Show raw data quality
    missing_count = df_raw.isnull().sum().sum()
    print(f"   Missing values: {missing_count}")
    print()
    
    # ===== STEP 2: TRANSFORM (Clean) =====
    print("🧹 STEP 2: TRANSFORM (Cleaning)")
    print("-" * 40)
    
    processor = DataProcessor(df_raw)
    processor.clean()
    
    # Verify cleaning
    missing_after = processor.df.isnull().sum().sum()
    print(f"   ✅ Missing values after cleaning: {missing_after}")
    print(f"   ✅ Duplicate dates removed")
    print(f"   ✅ Data sorted by date")
    print()
    
    # ===== STEP 3: TRANSFORM (Features) =====
    print("⚙️  STEP 3: TRANSFORM (Feature Engineering)")
    print("-" * 40)
    
    processor.add_features()
    
    # List new features
    original_cols = set(df_raw.columns)
    new_cols = [col for col in processor.df.columns if col not in original_cols]
    print(f"   ✅ New features added: {new_cols}")
    
    # Show feature statistics
    if 'MA5' in processor.df.columns:
        ma5_valid = processor.df['MA5'].notna().sum()
        print(f"   MA5:  {ma5_valid} valid values (first 4 are NaN)")
    
    if 'MA20' in processor.df.columns:
        ma20_valid = processor.df['MA20'].notna().sum()
        print(f"   MA20: {ma20_valid} valid values (first 19 are NaN)")
    
    if 'Vol_20' in processor.df.columns:
        vol_valid = processor.df['Vol_20'].notna().sum()
        print(f"   Vol_20: {vol_valid} valid values")
    
    print()
    
    # ===== STEP 4: LOAD =====
    print("💾 STEP 4: LOAD")
    print("-" * 40)
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"   Created directory: {output_dir}")
    
    try:
        processor.save_to_parquet(output_path)
    except Exception as e:
        print(f"   ❌ Error saving file: {e}")
        return None
    
    print()
    
    # ===== SUMMARY =====
    print("=" * 60)
    print("        📊 PIPELINE SUMMARY")
    print("=" * 60)
    print()
    
    df_final = processor.get_dataframe()
    
    print(f"📋 Final Data Shape: {df_final.shape[0]} rows × {df_final.shape[1]} columns")
    print()
    
    if 'date' in df_final.columns:
        print(f"📅 Date Range:")
        print(f"   Start: {df_final['date'].min()}")
        print(f"   End:   {df_final['date'].max()}")
        print()
    
    if 'close' in df_final.columns:
        print(f"💰 Price Range:")
        print(f"   Min:  {df_final['close'].min():.2f}")
        print(f"   Max:  {df_final['close'].max():.2f}")
        print()
    
    print(f"📈 Columns in output:")
    for i, col in enumerate(df_final.columns, 1):
        print(f"   {i}. {col}")
    print()
    
    # Preview
    print("🔍 Data Preview (first 5 rows):")
    print("-" * 60)
    preview_cols = ['date', 'close', 'MA5', 'MA20', 'Vol_20']
    preview_cols = [c for c in preview_cols if c in df_final.columns]
    print(df_final[preview_cols].head().to_string(index=False))
    print("-" * 60)
    print()
    
    print("✅ ETL Pipeline completed successfully!")
    print("=" * 60)
    print()
    
    return df_final


def verify_output(output_path: str) -> bool:
    """
    Verify the output file can be read correctly.
    
    Args:
        output_path: Path to the Parquet file
        
    Returns:
        True if verification passed, False otherwise
    """
    print("🔍 VERIFICATION")
    print("-" * 40)
    
    try:
        df = pd.read_parquet(output_path)
        print(f"   ✅ File readable: {output_path}")
        print(f"   ✅ Rows: {len(df)}")
        print(f"   ✅ Columns: {list(df.columns)}")
        
        # Check key columns exist
        required_cols = ['date', 'close', 'MA5', 'MA20', 'Vol_20']
        missing_cols = [c for c in required_cols if c not in df.columns]
        
        if missing_cols:
            print(f"   ⚠️  Missing columns: {missing_cols}")
            return False
        
        print("   ✅ All required columns present")
        return True
        
    except Exception as e:
        print(f"   ❌ Verification failed: {e}")
        return False


def main():
    """Main entry point."""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Run ETL pipeline for stock data'
    )
    parser.add_argument(
        '--input', '-i',
        default='data/raw/stock_data_dirty.csv',
        help='Input CSV file path'
    )
    parser.add_argument(
        '--output', '-o',
        default='data/processed/market_data.parquet',
        help='Output Parquet file path'
    )
    parser.add_argument(
        '--verify', '-v',
        action='store_true',
        help='Verify output after processing'
    )
    
    args = parser.parse_args()
    
    # Run pipeline
    df = run_etl_pipeline(args.input, args.output)
    
    if df is None:
        print("❌ Pipeline failed!")
        sys.exit(1)
    
    # Verify if requested
    if args.verify:
        print()
        if not verify_output(args.output):
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
