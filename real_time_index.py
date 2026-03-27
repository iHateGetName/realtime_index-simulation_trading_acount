from xtquant import xtdatacenter as xtdc
from xtquant import xtdata  
import pandas as pd 
import random
import datetime
import tushare as ts
import os
import yaml
def load_config():
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)
    return config
config = load_config()
TUSHARE_API_KEY = config["api"]["tushare_api_key"]
XTQUANT_API_KEY = config["api"]["xtquant_api_key"]
ts.set_token(TUSHARE_API_KEY)
pro = ts.pro_api(TUSHARE_API_KEY)
# xtdc.set_token("857b1fa0068599ccb191546f86bac28e09d8a727") # 试用过期
xtdc.set_token(XTQUANT_API_KEY)
xtdc.set_data_home_dir("../xtquant_tushare/srv/xuntoudata/data")
xtdc.init(False)
actual_port = random.randint(58600,58700)
xtdc.listen(port=actual_port)
print(f"服务启动,开放端口：{actual_port}")

def get_prev_trade_date(date): # 函数从当前日期往回找，直到找到一个交易日
    prev_day =(pd.to_datetime(date) - pd.Timedelta(days=1)).strftime('%Y%m%d')
    while True:
        if int(pro.trade_cal(exchange='SSE', start_date=prev_day, end_date=prev_day)['is_open'][0]) == 1:
            return prev_day
        else :
            prev_day =(pd.to_datetime(prev_day) - pd.Timedelta(days=1)).strftime('%Y%m%d')
def get_closePrice_and_weight_from_csv(index_code,last_trade_day): # 从csv文件中获取上一个交易日的成分股权重和收盘价    
    file_dir = ""
    for filedir in os.listdir(f'./ref/project_/cal_index_data/'):
        if index_code in filedir:
            file_dir = filedir
            break
    
    last_date_info = pd.read_csv(f'./ref/project_/cal_index_data/{file_dir}/cal_weight_df_{index_code}_{last_trade_day}_副本.csv')
    print(f'读取文件cal_weight_df_{index_code}_{last_trade_day}_副本.csv')
    weight_dict = last_date_info.set_index('code')[f'{last_trade_day}weight'].to_dict()
    P_base_dict = last_date_info.set_index('code')[f'{last_trade_day}close'].to_dict()
    print(f"今天是{pd.Timestamp(datetime.datetime.now()).date().strftime('%Y%m%d')}，上一个交易日为{last_trade_day}")
    print(f'成分股权重{weight_dict}')
    print(f'成分股收盘价{P_base_dict}')
    return weight_dict, P_base_dict
def get_index_closePrice(index_code,last_trade_day): # 获取last_trade_day的指数的收盘价
    xtdata.download_history_data(index_code,period='1d',start_time=last_trade_day, end_time='') 
    index_data = xtdata.get_market_data_ex([],[index_code],period='1d')
    I_base = float(index_data[index_code].loc[f'{last_trade_day}']['close'])
    print(f'{index_code}的{last_trade_day}的收盘价为{I_base}')
    return I_base
# 计算实时指数和实时基差

def get_realtime_computing_index(index_code,I_base,P_base_dict,weight_dict,CFE_code,multiple_factor = 200): 
    # 函数参数要注意这个指数和后面的前一天收盘价还有成分股收盘价字典以及权重字典要日期、内容对应。CFE_list是指期货合约代码列表，用来算实时基差
    S_t = 0
    stocks_buy_amount = {}
    code_list = list(weight_dict.keys())
    code_data = xtdata.get_full_tick(code_list)
    real_time_index_data = xtdata.get_full_tick([index_code,CFE_code])
    real_time_index = real_time_index_data[index_code]['lastPrice']
    for code in code_list:
        P_t = code_data[code]['lastPrice']
        P_base = P_base_dict[code]
        W_base = weight_dict[code]
        stocks_buy_amount[code] = int(round((W_base * (multiple_factor * real_time_index) / P_t)/100)) if code_data[code]['stockStatus'] == 3 else int(round((W_base * (multiple_factor * real_time_index) / P_base) /100))
        S_t += W_base * (P_t / P_base) if code_data[code]['stockStatus'] == 3 else W_base 
    I_t = I_base * (S_t / 100)
    print(f'实时推送指数为{real_time_index},计算指数I_t为{I_t},误差为{real_time_index - I_t}，误差率为{(real_time_index - I_t) / real_time_index}')
    print(f"{CFE_code}的当前价格为{real_time_index_data[CFE_code]['lastPrice']}，推送基差为{real_time_index-real_time_index_data[CFE_code]['lastPrice']},计算基差为{I_t-real_time_index_data[CFE_code]['lastPrice']}")
    return I_t-real_time_index_data[CFE_code]['lastPrice'],stocks_buy_amount

def read_last_trade_day_data_for_prepare_to_get_realtime_basis(index_code):
    now_date = pd.Timestamp(datetime.datetime.now()).date().strftime('%Y%m%d')
    last_trade_day = get_prev_trade_date(now_date)
    weight_dict,P_base_dict = get_closePrice_and_weight_from_csv(index_code,last_trade_day)
    I_base = get_index_closePrice(index_code,last_trade_day)
    return I_base,P_base_dict,weight_dict

CFE_code = 'IM2604.IF'
index_code = '000852.SH'
I_base,P_base_dict,weight_dict = read_last_trade_day_data_for_prepare_to_get_realtime_basis(index_code)
realtime_basis,stocks_buy_amount = get_realtime_computing_index(index_code,I_base,P_base_dict,weight_dict,CFE_code,200)
