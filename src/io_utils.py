"""
io_utils.py - 文件读写工具
提供 CSV 文件的读取和保存功能
"""

import pandas as pd
import os


def read_csv(path):
    """
    读取 CSV 文件
    
    参数:
        path: 文件路径（字符串）
        
    返回:
        DataFrame: 表格数据
        
    异常:
        如果文件不存在，抛出友好的错误提示
    """
    # 检查文件是否存在
    if not os.path.exists(path):
        raise FileNotFoundError(f"文件不存在: {path}")
    
    # 读取 CSV 并返回
    df = pd.read_csv(path)
    return df


def save_csv(df, path):
    """
    保存数据到 CSV 文件
    
    参数:
        df: 要保存的 DataFrame
        path: 保存路径（字符串）
    """
    # 确保目录存在（如果不存在就创建）
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    # 保存文件（index=False 表示不保存行号）
    df.to_csv(path, index=False)
    print(f"文件已保存: {path}")
