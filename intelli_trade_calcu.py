from datetime import datetime,timedelta
import pandas as pd


def calculate_kdj(data, n=9, m1=3, m2=3):
    # 计算RSV（未成熟随机指标）
    data['low_n'] = data['low'].rolling(window=n, min_periods=1).min()
    data['high_n'] = data['high'].rolling(window=n, min_periods=1).max()
    data['RSV'] = (data['close'] - data['low_n']) / (data['high_n'] - data['low_n']) * 100
    # 计算K值、D值、J值
    data['KDJ_K'] = data['RSV'].ewm(com=m1 - 1).mean()
    data['KDJ_D'] = data['KDJ_K'].ewm(com=m2 - 1).mean()
    data['KDJ_J'] = 3 * data['KDJ_K'] - 2 * data['KDJ_D']
    # 移除辅助列
    data.drop(['low_n', 'high_n', 'RSV'], axis=1, inplace=True)
    return data

# 假设有一个包含股价的 DataFrame，其中列名为 'Date' 和 'Close'
# 示例数据，实际应用时需要替换为实际数据


def calculate_ma_offset(df):

    # data = {'Date': pd.date_range(start=startTime, periods=periods),
    #         'Close': [100, 105, 110, 95, 90, 92, 105, 108, 112, 115]}
    # df = pd.DataFrame(data)

    # 计算五日均线
    df['MA5'] = df['close'].rolling(window=5).mean()
    df['MA10'] = df['close'].rolling(window=10).mean()
    df['MA20'] = df['close'].rolling(window=20).mean()
    df['MA30'] = df['close'].rolling(window=30).mean()

    # 计算乖离率
    df['乖离率5'] = (df['open'] - df['MA5']) / df['MA5'] * 100
    df['乖离率10'] = (df['open'] - df['MA10']) / df['MA10'] * 100
    df['乖离率20'] = (df['open'] - df['MA20']) / df['MA20'] * 100
    df['乖离率30'] = (df['open'] - df['MA30']) / df['MA30'] * 100

    # print(df)
    return df


# 示例数据
# data = pd.DataFrame({
#     'date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
#     'open': [100, 102, 98, 105, 110],
#     'high': [105, 110, 100, 112, 115],
#     'low': [98, 100, 95, 98, 100],
#     'close': [102, 108, 98, 110, 112],
# })

# data['date'] = pd.to_datetime(data['date'])
# data.set_index('date', inplace=True)
#
# # 计算KDJ指标
# result = calculate_kdj(data)
#
# # 输出结果
# print(result[['KDJ_K', 'KDJ_D', 'KDJ_J']])
#
#
# dateRang = pd.date_range(start=(datetime.now()-timedelta(days=10)).strftime("%Y-%m-%d"), periods=10)
# print(dateRang)