# 实时基差计算/模拟交易

## requirements
- tushare
- xtquant
- pandas
- pyyaml



## 项目介绍
本项目基于tushare和xtquant库，实时计算股票指数的基差值，并模拟交易。目前项目包含四个Jupyter Notebook文件，用于处理指数权重数据、计算最新权重以及实时计算指数和基差。这些工具可以帮助用户根据官方发布的权重文件，计算并更新指数成分股的权重，以及实时监控指数表现。

## 用法介绍/文件说明
### 1. 配置API
用户需将自己的tushare和迅投API密钥配置在`config.py`文件中。
### 2. 从官网获取初始权重文件
用户可从中证官网下载各指数权重文件。中证官网地址:https://www.csindex.com.cn
### 3. 运行"给官方权重添加收盘价.ipynb"文件
在该文件中，用户需要修改file_path变量为下载的指数权重文件路径，然后全部运行。运行之后，会在路径./ref/project_/cal_index_data下得到一个{index_name}_{index_code}文件夹，里面有{index_code}_{weight_start_date} - 副本.csv文件。
### 4. 运行"cal_weight.ipynb"文件
在该文件中，用户需要修改index_code和weight_start_date，这两个变量需要和第二步中下载的权重文件里面的"日期date"和"指数代码Index Code"保持一致。其中index_code要加上后缀。然后全部运行，运行完后会在{index_name}_{index_code}文件夹中得到cal_weight_df_{index}_{last_trade_day}.csv文件。
### 5. 运行"real_time_index.ipynb"文件
用户需要修改index_code。然后全部运行，get_realtime_computing_index函数会实时计算指数和基差值。

## 关于模拟交易功能，trading_account.ipynb文件
该文件中有模拟现实交易账户的类TradingAccount。里面有如下函数：
- __init__: 初始化交易账户，设置账户余额。
- get_current_price: 获取商品当前市价
- get_instrument_type: 获取商品类型
- get_instructment_details: 获取商品详情
- buy: 购买股票(用于交易股票，基金)
- sell: 卖出股票(用于交易股票，基金)
- transfer_to_futures_position: 将仓外余额转到期货仓内，该设计单独分了一个期货仓，只有期货仓里的金额可用于期货交易
- transfer_out_futures_position: 将期货仓余额转到仓外
- open_a_futures_position: 开仓期货(用于交易期货)
- close_a_futures_position: 平仓期货(用于交易期货)
- clear_inventory: 清空某类商品所有持仓
- auto_trade_stock: 自动监控交易股票，需设定买入价格，止损卖出价格，止盈卖出价格
- stop_auto_trade_stock: 停止自动交易股票

用户可以运行print(类对象)来查看当前持仓、订单、账户余额等信息。


**代码**
```
  期货高手 = TradingAccount("kmbzg144", 2000000.0)
  期货高手.transfer_to_futures_position(1000000.0)
  期货高手.buy("300383.SZ",10000)
  期货高手.open_a_futures_position("IM2604.IF",1,"go_short")
  print(期货高手)
```

**结果**
```
  以182300.00成交10000股300383.SZ
  以183600.00保证金成交1手IM2604.IF，合约价值：1530000.00
  账号: kmbzg144
  仓外余额: 817700.00
  仓内市值 + 期货盈亏: 182300.000
  期货仓余额: 1000000.000
  被冻结保证金: 183600.000
  总资产: 2000000.000
  持仓:
    STOCK 300383.SZ:
      最近交易时间: 2026-03-25 16:55:19
      买入时市价: 18.230
      持仓量: 10000
      买入金额: 182300.00
      当前市价: 18.230
      当前仓位市值: 182300.000
      当前盈亏比: 0.0000
    FUTURES IM2604.IF_go_short:
      最近交易时间: 2026-03-25 16:55:20
      交易方向: go_short
      持仓量: {7650.0: 1}
      冻结保证金: 183600.00
      当前指数价格: 7650.000
      当前合约市价: 1530000.000
      当前盈亏: 0.000
      当前风险度: 0.1836
```