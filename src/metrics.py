"""
metrics.py - 量化指标计算工具
提供均值、标准差、最大回撤等计算函数
"""


def mean(x):
    """
    计算均值（平均数）
    
    参数:
        x: 数字列表，如 [1, 2, 3]
        
    返回:
        float: 均值
    """
    # 边界情况：空列表
    if len(x) == 0:
        return 0.0
    
    # 求和 / 个数
    total = sum(x)
    count = len(x)
    return total / count


def std(x):
    """
    计算总体标准差
    
    参数:
        x: 数字列表
        
    返回:
        float: 标准差
        
    注意:
        这里用的是「总体标准差」，除以 n
        （另一种「样本标准差」是除以 n-1）
    """
    # 边界情况
    if len(x) == 0:
        return 0.0
    if len(x) == 1:
        return 0.0
    
    # 1. 计算均值
    avg = mean(x)
    
    # 2. 计算每个值与均值的差的平方
    squared_diffs = [(val - avg) ** 2 for val in x]
    
    # 3. 求平均（方差）
    variance = sum(squared_diffs) / len(x)
    
    # 4. 开根号得到标准差
    result = variance ** 0.5
    return result


def max_drawdown(nav_series):
    """
    计算最大回撤
    
    参数:
        nav_series: 净值序列，如 [1.0, 1.1, 1.05, 1.2, 1.0]
        
    返回:
        float: 最大回撤比例（0到1之间）
        
    原理:
        遍历每个点，记录到目前为止的最高点（峰值）
        计算当前点相对于峰值的跌幅
        取所有跌幅中的最大值
    """
    # 边界情况
    if len(nav_series) == 0:
        return 0.0
    if len(nav_series) == 1:
        return 0.0
    
    max_dd = 0.0      # 最大回撤（初始为0）
    peak = nav_series[0]  # 历史最高点（初始为第一个值）
    
    # 遍历每个净值
    for nav in nav_series:
        # 如果当前值比之前的最高点还高，更新最高点
        if nav > peak:
            peak = nav
        
        # 计算当前回撤：(最高点 - 当前值) / 最高点
        if peak > 0:  # 避免除以0
            drawdown = (peak - nav) / peak
            
            # 如果这次回撤更大，更新最大回撤
            if drawdown > max_dd:
                max_dd = drawdown
    
    return max_dd
