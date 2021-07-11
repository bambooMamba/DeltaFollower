# -*- coding: utf-8 -*-#
"""
@File    :   stock.py    
@Contact :   sheng_jun@yeah.net
@Author  :   Ace
@Description: 
@Modify Time      @Version    @Desciption
------------      --------    -----------
2021-06-30 0:47    1.0         None
"""
import time
import pandas as pd
from acquire.config import api
from datetime import datetime
import os
from util import response
from util import location


def _get_from_waditu(api_name, fields: str = '', **kwargs):
    return response.get_from_waditu(api_name, fields, **kwargs)


class BasicInfo:
    """
    @Desc:描述A股市场的股票基本信息，包括：股票列表
    @Maybe:之后可能会继续增加成分股，上市公司基本信息，交易所日历，IPO等信息
    """

    def __init__(self):
        self.stock_basic = _get_from_waditu(api_name="stock_basic", fields="ts_code,symbol,name,industry,list_date")
        self.ts_code_list = list(self.stock_basic["ts_code"])
        self.symbol_list = list(self.stock_basic["symbol"])
        self.name_list = list(self.stock_basic["name"])
        self.start_date_list = list(self.stock_basic["list_date"])
        self.code2name = dict(zip(self.ts_code_list, self.name_list))
        self.name2code = dict(zip(self.name_list, self.ts_code_list))
        self.code2symbol = dict(zip(self.ts_code_list, self.symbol_list))
        self.symbol2code = dict(zip(self.symbol_list, self.ts_code_list))
        self.code2start = dict(zip(self.ts_code_list, self.start_date_list))


class History:
    """
    @Desc：获取整个A股市场的历史数据
    数据分两快：basic，price
    """

    def __init__(self, code_date, root):
        self.code_date = code_date
        self.root = root

    def save_basic_price_data(self):
        today = datetime.today().strftime("%Y%m%d")
        for ts_code, start_time in self.code_date.items():
            price_df = _get_from_waditu(api_name="daily", ts_code=ts_code, start_date=start_time, end_date=today, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
            last_date = price_df.iloc[-1, 1]
            if last_date > start_time:
                next_df = _get_from_waditu(api_name="daily", ts_code=ts_code, start_date=start_time, end_date=last_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
                price_df = price_df.append(next_df, ignore_index=True)
            price_df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)

            basic_df = _get_from_waditu(api_name="daily_basic", ts_code=ts_code, start_date=start_time, end_date=today)
            last_date = basic_df.iloc[-1, 1]
            if last_date > start_time:
                next_df = _get_from_waditu(api_name="daily_basic", ts_code=ts_code, start_date=start_time, end_date=last_date)
                basic_df = basic_df.append(next_df, ignore_index=True)
            basic_df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
            location.save_csv(ts_code=ts_code, df=price_df, root=self.root)
            location.save_csv(ts_code=ts_code, df=basic_df, root=self.root, kind="daily/basic/")


class Single:
    """
    @Desc：获取个股数据，包括日线数据，曾用名，每日指标
    @Maybe：各种财务数据
    """

    def __init__(self, ts_code, start_date=datetime.today().strftime("%Y%m%d"), end_date=datetime.today().strftime("%Y%m%d")):
        self.start_date = start_date
        self.end_date = end_date
        self.ts_code = ts_code
        # self.daily_price = self._get_daily_price()
        # self.name_change_list = self._get_name_change_list()
        # self.daily_basic = self._get_daily_basic()

    def get_daily_price(self):
        df = _get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        last_date = df.iloc[-1, 1]
        if last_date > self.start_date:
            next_df = _get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=self.start_date, end_date=last_date, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
            df = df.append(next_df, ignore_index=True)
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)  # 因为获取到的数据是时间倒序的，所以我们要进行时间的重新排列
        return df

    def get_name_change_list(self):
        df = _get_from_waditu(api_name="namechange", ts_code=self.ts_code, fields="ts_code,name,start_date,end_date")
        # df["start_date"] = pd.to_datetime(df["start_date"])
        df.sort_values(by=["start_date"], inplace=True)
        return df

    def get_daily_basic(self):
        df = _get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date)
        last_date = df.iloc[-1, 1]
        if last_date > self.start_date:
            next_df = _get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=last_date)
            df = df.append(next_df, ignore_index=True)
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)  # 因为获取到的数据是时间倒序的，所以我们要进行时间的重新排列
        return df

    def get_recent_price(self, start_date_, end_date_):
        df = _get_from_waditu(api_name="daily", ts_code=self.ts_code, start_date=start_date_, end_date=end_date_, fields="ts_code,trade_date,open,high,low,close,pre_close,vol,amount")
        df.sort_values(by="trade_date", ascending=True, ignore_index=True, inplace=True)
        return df

    def get_recent_basic(self):
        df = _get_from_waditu(api_name="daily_basic", ts_code=self.ts_code, start_date=self.start_date, end_date=self.end_date)
        return df


class Location:
    """
    @ 从本地获取基础数据数据，根据基础数据获得所需形状的数据，计算adj等
    """

    def __init__(self, root, ts_code, kind="price"):
        self.read_path = "%sdaily/%s/%s.csv" % (root, kind, ts_code)
        self.ts_code = ts_code
        self.kind = kind

    def get_single_data(self):
        # 获取到的数据还是比较干净，但是为了严谨，我们还是有必要做一些去重的清理工作和时间解析工作，以保证客户得到的数据是以时间序列为基准的
        df = pd.read_csv(filepath_or_buffer=self.read_path, parse_dates=["trade_date"])
        df.sort_values(by=["trade_date"], inplace=True)
        df.drop_duplicates(subset=["trade_date"], inplace=True)
        df.reset_index(drop=True, inplace=True)
        # df["trade_date"] = pd.to_datetime(df["trade_date"])
        # df.set_index(keys=["trade_date"], inplace=True)
        return df

    def calc_adj_data(self):
        """
        计算复权价，复权因子
        :return:含有前复权、后复权“开高低收”，复权因子，涨跌幅的df
        """
        assert self.kind == "price", "计算股票复权价，类型必须为基础行情数据"
        df = self.get_single_data()
        df["pct_change"] = df["close"] / df["pre_close"] - 1
        df["adj_factor"] = (1 + df["pct_change"]).cumprod()
        df["hfq_close"] = df["adj_factor"] * (df.iloc[0]["close"] / df.iloc[0]["adj_factor"])
        df["qfq_close"] = df["adj_factor"] * (df.iloc[-1]["close"] / df.iloc[-1]["adj_factor"])
        # 复权收盘价 / 复权开盘价 = 收盘价 / 开盘价
        df["qfq_open"] = df["open"] / df["close"] * df["qfq_close"]
        df["qfq_high"] = df["high"] / df["high"] * df["qfq_close"]
        df["qfq_low"] = df["low"] / df["low"] * df["qfq_close"]
        # 同理可以计算后复权
        df["hfq_open"] = df["open"] / df["close"] * df["hfq_close"]
        df["hfq_high"] = df["high"] / df["high"] * df["hfq_close"]
        df["hfq_low"] = df["low"] / df["low"] * df["hfq_close"]
        return df

    # def save_daily_2_location(self, df: pd.DataFrame):
    #     kind_path = self.read_path
    #     mode = ""
    #     header = False
    #     if os.path.exists(kind_path):
    #         mode = "a"
    #     else:
    #         mode = "w"
    #         header = True
    #     df.to_csv(path_or_buf=kind_path, index=False, mode=mode, header=header)
    #     print("%s已存入---" % self.ts_code)