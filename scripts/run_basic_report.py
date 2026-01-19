"""
run_basic_report.py - 基础量化报告脚本

功能：
1. 读取价格数据
2. 计算收益率和净值
3. 计算统计指标
4. 打印报告
"""

import sys
import os

# 把项目根目录添加到 Python 路径（这样才能导入 src 下的模块）
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.io_utils import read_csv
from src.metrics import mean, std, max_drawdown


def calculate_returns(prices):
    """
    计算收益率序列
    
    参数:
        prices: 价格列表 [100, 102, 101, ...]
        
    返回:
        list: 收益率列表（比价格少一个元素）
    """
    returns = []
    for i in range(1, len(prices)):
        # 收益率 = (今天 - 昨天) / 昨天
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
    return returns


def calculate_nav(returns):
    """
    计算净值序列
    
    参数:
        returns: 收益率列表
        
    返回:
        list: 净值列表（从1.0开始）
    """
    nav = [1.0]  # 起始净值为 1
    for ret in returns:
        # 新净值 = 上一个净值 × (1 + 收益率)
        new_nav = nav[-1] * (1 + ret)
        nav.append(new_nav)
    return nav


def main():
    """主函数：执行完整的分析流程"""
    
    print("=" * 50)
    print("        📊 基础量化分析报告")
    print("=" * 50)
    print()
    
    # ===== 1. 读取数据 =====
    data_path = "data/raw/sample_prices.csv"
    print(f"📂 读取数据: {data_path}")
    
    try:
        df = read_csv(data_path)
    except FileNotFoundError as e:
        print(f"❌ 错误: {e}")
        return
    
    print(f"   共 {len(df)} 条记录")
    print()
    
    # ===== 2. 提取价格数据 =====
    prices = df['close'].tolist()  # 转换为列表
    dates = df['date'].tolist()
    
    print("📈 价格数据预览:")
    print(f"   起始日期: {dates[0]}, 价格: {prices[0]}")
    print(f"   结束日期: {dates[-1]}, 价格: {prices[-1]}")
    print()
    
    # ===== 3. 计算收益率 =====
    returns = calculate_returns(prices)
    print("📊 收益率统计:")
    print(f"   交易天数: {len(returns)} 天")
    print(f"   日均收益率: {mean(returns) * 100:.4f}%")
    print(f"   收益率波动率: {std(returns) * 100:.4f}%")
    print()
    
    # ===== 4. 计算净值和最大回撤 =====
    nav = calculate_nav(returns)
    mdd = max_drawdown(nav)
    
    print("💰 净值分析:")
    print(f"   起始净值: {nav[0]:.4f}")
    print(f"   最终净值: {nav[-1]:.4f}")
    print(f"   总收益率: {(nav[-1] - 1) * 100:.2f}%")
    print(f"   最大回撤: {mdd * 100:.2f}%")
    print()
    
    # ===== 5. 总结 =====
    print("=" * 50)
    print("📋 总结")
    print("=" * 50)
    print(f"   • 日均收益: {mean(returns) * 100:.4f}%")
    print(f"   • 波动率:   {std(returns) * 100:.4f}%")
    print(f"   • 总收益:   {(nav[-1] - 1) * 100:.2f}%")
    print(f"   • 最大回撤: {mdd * 100:.2f}%")
    print("=" * 50)


# 这是 Python 的标准写法：当直接运行这个脚本时，执行 main()
if __name__ == "__main__":
    main()
