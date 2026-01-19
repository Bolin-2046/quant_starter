"""
test_metrics.py - metrics.py 的测试用例

运行方式：
    pytest tests/test_metrics.py -v

测试覆盖：
    - mean(): 均值计算
    - std(): 标准差计算
    - max_drawdown(): 最大回撤计算
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.metrics import mean, std, max_drawdown


# ============================================================
# 测试 mean() 函数
# ============================================================

def test_mean_normal():
    """测试正常情况的均值计算"""
    result = mean([1, 2, 3, 4, 5])
    expected = 3.0
    assert result == expected, f"期望 {expected}，实际 {result}"


def test_mean_single_value():
    """测试只有一个值的情况"""
    result = mean([42])
    expected = 42.0
    assert result == expected


def test_mean_empty():
    """测试空列表"""
    result = mean([])
    expected = 0.0
    assert result == expected


def test_mean_negative():
    """测试包含负数的情况"""
    result = mean([-1, 0, 1])
    expected = 0.0
    assert result == expected


# ============================================================
# 测试 std() 函数
# ============================================================

def test_std_normal():
    """测试正常情况的标准差"""
    result = std([1, 2, 3])
    # 手算：均值=2, 方差=((1-2)²+(2-2)²+(3-2)²)/3 = 2/3, 标准差=√(2/3)≈0.8165
    expected = 0.816496580927726
    # 浮点数比较要用近似相等
    assert abs(result - expected) < 0.0001, f"期望 {expected}，实际 {result}"


def test_std_no_variance():
    """测试所有值相同（无波动）"""
    result = std([5, 5, 5, 5])
    expected = 0.0
    assert result == expected


def test_std_empty():
    """测试空列表"""
    result = std([])
    expected = 0.0
    assert result == expected


def test_std_single_value():
    """测试只有一个值"""
    result = std([100])
    expected = 0.0
    assert result == expected


# ============================================================
# 测试 max_drawdown() 函数
# ============================================================

def test_max_drawdown_normal():
    """测试正常情况的最大回撤"""
    # 净值从1.0涨到1.2，然后跌到0.9
    nav = [1.0, 1.2, 1.1, 0.9, 1.0]
    result = max_drawdown(nav)
    # 最大回撤 = (1.2 - 0.9) / 1.2 = 0.25
    expected = 0.25
    assert abs(result - expected) < 0.0001


def test_max_drawdown_always_up():
    """测试一直上涨（没有回撤）"""
    nav = [1.0, 1.1, 1.2, 1.3, 1.4]
    result = max_drawdown(nav)
    expected = 0.0
    assert result == expected


def test_max_drawdown_always_down():
    """测试一直下跌"""
    nav = [1.0, 0.9, 0.8, 0.7]
    result = max_drawdown(nav)
    # 最大回撤 = (1.0 - 0.7) / 1.0 = 0.3
    expected = 0.3
    assert abs(result - expected) < 0.0001


def test_max_drawdown_empty():
    """测试空列表"""
    result = max_drawdown([])
    expected = 0.0
    assert result == expected


def test_max_drawdown_single_value():
    """测试只有一个值"""
    result = max_drawdown([1.0])
    expected = 0.0
    assert result == expected


def test_max_drawdown_example_from_task():
    """测试任务书里给的例子"""
    # 任务书例子：[1.0, 1.1, 1.05, 1.2, 1.0]
    nav = [1.0, 1.1, 1.05, 1.2, 1.0]
    result = max_drawdown(nav)
    # 最高点是1.2，最低点是1.0，回撤 = (1.2-1.0)/1.2 = 0.1666...
    expected = 0.16666666666666666
    assert abs(result - expected) < 0.0001


# ============================================================
# 运行测试（如果直接运行这个文件）
# ============================================================

if __name__ == "__main__":
    print("请使用 pytest 运行测试：")
    print("  pytest tests/test_metrics.py -v")
