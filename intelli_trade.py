import os
from datetime import datetime, timedelta, time

import akshare as ak
import intelli_trade_calcu
import sys
import time as time1
import pandas as pd


file_path = "./output.txt"
def custom_stock():
    #判断代码文件中是否还有未分析的数据
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding="utf-8") as file:
            lines = file.readlines()  # 读取所有行，返回一个列表
            print(f"从文件中获取：{len(lines)}")
            if len(lines) > 0:
                data_dict = {}
                for line in lines:
                    print(line)
                    # 去掉行尾的换行符并按制表符分割
                    key, stock_name = line.strip().split('\t')
                    data_dict[key] = stock_name
                return data_dict
    # 全量stock
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    # print(stock_zh_a_spot_em_df)
    df = pd.DataFrame(stock_zh_a_spot_em_df)
    filterStockDf = df[(df["总市值"] > 110 * 100000000) & (df["总市值"] < 150*100000000) &
                       (df["市盈率-动态"] > 0) &
                       (~df["名称"].str.contains(r'^(ST|[*]ST|N|C)', regex=True)) &
                       (~df["代码"].astype(str).str.startswith("8"))]
    result_dict = filterStockDf[["代码", "名称"]].set_index("代码")["名称"].to_dict()

    print("总数为：" + str(len(result_dict)) + "\n")
    # 创建并写入文件
    with open('output.txt', 'w', encoding="utf-8") as file:  # 'w' 模式表示新建文件（如果文件已存在，会覆盖）
        for stock_key, stock_name in result_dict.items():
            stock_name_bytes = stock_name.encode("utf-8")
            stock_name = stock_name_bytes.decode("utf-8")
            # sys.exit(4)
            file.write(f"{stock_key}\t{stock_name}\n")  # 使用 \n 换行
    return result_dict

# 示例数据
# data = pd.DataFrame({
#     'date': ['2022-01-01', '2022-01-02', '2022-01-03', '2022-01-04', '2022-01-05'],
#     'open': [100, 102, 98, 105, 110],
#     'high': [105, 110, 100, 112, 115],
#     'low': [98, 100, 95, 98, 100],
#     'close': [102, 108, 98, 110, 112],
# })
def calcu(stock_zh_a_hist_df, item, name):
    global excel_data
# 计算kdj需要的格式
    kdjRawData = pd.DataFrame({
        'code': item,
        'name': name,
        'date': stock_zh_a_hist_df['日期'],
        'close': stock_zh_a_hist_df['收盘'],
        'open': stock_zh_a_hist_df['最高'],
        'high': stock_zh_a_hist_df['最高'],
        'low': stock_zh_a_hist_df['最低'],
    })

    # kdjRawData['date'] = pd.to_datetime(kdjRawData['date'])
    # # print(type(kdjRawData['date']))
    # kdjRawData.set_index('date', inplace=True)

    # 计算KDJ指标
    kdjResult = intelli_trade_calcu.calculate_kdj(kdjRawData)
    kdjResult = kdjResult.drop(['close', 'high', 'low'], axis=1)
    # print(type(kdjResult))
    # print(kdjResult)

    # 输出kdj结果
    # print(kdjResult[['KDJ_K', 'KDJ_D', 'KDJ_J']])

    # ma乖离率
    maRawData = pd.DataFrame({
        'date': stock_zh_a_hist_df['日期'],
        'close': stock_zh_a_hist_df['收盘'],
        'open': stock_zh_a_hist_df['开盘'],
        'amount': stock_zh_a_hist_df['成交量']
    })
    maResult = intelli_trade_calcu.calculate_ma_offset(maRawData)

    # print(maResult)
    # print(type(maResult))
    mergedData = pd.merge(maResult, kdjResult, on='date', how='inner')
    print(mergedData)
    excel_data = pd.concat([excel_data, mergedData], axis=0)
    # 全量stock
    # stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    # print(stock_zh_a_spot_em_df)
    # df = pd.DataFrame(stock_zh_a_spot_em_df)
    # df.to_excel('stock_code.xlsx', index=False)

    # 历史 1.拉取所有stock代码 ;2 循环获取每一个 stock的 $20天 数据 3 计算每一个stock 距离 ma$5 的乖离率, kdj的值
    # stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol="301302", period="daily", start_date="20231201", end_date='20240123', adjust="hfq")
    # # print(stock_zh_a_hist_df)
    # df = pd.DataFrame(stock_zh_a_hist_df)
    # df.to_excel('301302.xlsx', index=False)

#删除第一行
def remove_first_line(file_path):
    # 打开文件并读取所有行
    with open(file_path, 'r', encoding="utf-8") as file:
        lines = file.readlines()

    # 如果文件中有内容，删除第一行
    if lines:
        lines = lines[1:]

    # 将剩余行写回文件
    with open(file_path, 'w', encoding="utf-8") as file:
        file.writelines(lines)

#导出5天数据
period = 5

currentTime = datetime.now().time()
tradeTime = time(15, 0, 0)
#5*12 天的历史数据
startDate = (datetime.now() - timedelta(days=period*12)).strftime("%Y%m%d")

print(startDate)
# exit()
if currentTime < tradeTime:
    endDate = (datetime.now()-timedelta(days=1)).strftime("%Y%m%d")
else:
    endDate = datetime.now().strftime("%Y%m%d")

print(endDate)
# 手动指定stock code
if len(sys.argv) > 1:
    stockCode = {sys.argv[1]: ''}
else:
    stockCode = custom_stock()    #获取目标池
    print(f"总数为：{len(stockCode)}")
    # sys.exit(33)


# 原始数据
file_name = datetime.now().strftime('%Y%m%d%H%M%S')
count = 0
stock_zh_a_hist_df = pd.DataFrame()
excel_data = pd.DataFrame()
for item, value in stockCode.items():
    # print(item)
    time1.sleep(1)
    try:
        stock_zh_a_hist_df = ak.stock_zh_a_hist(symbol=item, period="daily", start_date=startDate, end_date=endDate, adjust ="qfq")
    except Exception as e:
        print(f"wale-error:{e}")
        excel_data.to_excel(file_name + '.xlsx', index=False)
        sys.exit(2)
    # print(stock_zh_a_hist_df)
    if stock_zh_a_hist_df.empty:
        remove_first_line(file_path)
        continue
    calcu(stock_zh_a_hist_df, item, value)
    remove_first_line(file_path)
    count += 1
    print(f"执行到了： {count} \n")
    # if count == 3:
    #     break
excel_data.to_excel(file_name + '.xlsx', index=False)

# exit()