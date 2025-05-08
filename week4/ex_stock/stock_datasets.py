import FinanceDataReader as fdr
import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.holiday import AbstractHolidayCalendar,Holiday, USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay


def get_stock(p_code, p_start, p_end):
    df = fdr.DataReader(p_code,p_start,p_end)
    # df['Close'].plot()
    # plt.show()
    # 0 ~ 인덱스 초기화 (기존 인덱스는 컬럼으로 됨)
    df = df.reset_index()
    # 날짜 년월일
    seq = df['index'].dt.strftime('%Y-%m-%d')
    x_data = df[['Close']].astype(str)
    x_data['Date'] = seq
    file_nm = f"{p_code}_{p_start.replace('-','')}_{p_end.replace('-','')}.xlsx"
    x_data.to_excel(file_nm)

# get_stock('TSLA', '2019-01-01','2025-03-31')
class KoreaHoliday(AbstractHolidayCalendar):
    rules = [
        Holiday("설연휴", month=1, day=27),
        Holiday("임시공휴(삼일절)", month=3, day=3)
    ]
korea_bday = CustomBusinessDay(calendar=KoreaHoliday())
usa_bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())
yesterday = pd.Timestamp.today().normalize() - korea_bday

fifty_ago = yesterday - 50 * korea_bday
usa_fifty_ago = yesterday - 50 * usa_bday
print(yesterday.strftime('%Y-%m-%d'))
print(fifty_ago.strftime('%Y-%m-%d'))
print('usa',usa_fifty_ago.strftime('%Y-%m-%d'))

bizdays = pd.date_range(start='2025-02-10'
                , end='2025-04-21', freq=korea_bday)
print(bizdays)
get_stock('TSLA', '2025-02-07', '2025-04-21')
