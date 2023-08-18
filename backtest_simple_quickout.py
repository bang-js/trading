##############
# 털고 나가기 : 1h KOSDAQ
# MA5>60 매수
# MA5<60 매도
# +10% 이상 달성 익절
# -7% 폭락 시 손절

# import numpy as np
import pandas as pd
import numpy as np
import yfinance as yf
import datetime

#############
## ver 1. retrieve old and constructed data
# # ETF 선택
# ticker = 'TQQQ_tot'
# # csv 파일 불러오기
# df = pd.read_csv('C:/finance_backtest/{}.csv'.format(ticker))
#############

#############
## ver 2. retrieve online data
def retrieve_data(ticker, start_date, end_date, date_type='daily'):
    '''
    This function is to retrieve yahoo finance data and to preprocess the dataframe.
    Parameters:

    date_type: 'daily' (default) or 'weekly'
    '''
    # Retrieve TQQQ data
    df = yf.download(ticker, start=start_date, end=end_date)
    if date_type == 'daily':
        # change format to match the old data
        df.reset_index(inplace=True)
        col_rename = {'Date':'date', 'Open': 'open', 'Close': 'close'}
        df = df.rename(columns=col_rename)
    
    elif date_type == 'weekly':
        df = df.resample('W', closed='right').mean()
        
        # change format to match the old data
        df.reset_index(inplace=True)
        col_rename = {'Date':'date', 'Open': 'open', 'Close': 'close'}
        df = df.rename(columns=col_rename)

        # revise last index to the today
        df.loc[df.index[-1], 'date'] = datetime.datetime.today()
    
    return df

# set parameters
ticker = 'TQQQ'
start_date = "2022-07-01"
end_date = "2023-08-17"
date_type='daily'

# retrieve data
df = retrieve_data(ticker = ticker, start_date = start_date, end_date = end_date, date_type=date_type)

# MA signal 기준 설정
long = 50
short = 1
print(long, short)

# 필요한 column 생성
df['MA60'] = df['close'].rolling(long).mean()
df['MA5'] = df['close'].rolling(short).mean()
df['60>5'] = np.where(df['MA5']<df['MA60'],True,False)
df['ror'] = df['close']/df['close'].shift(1) - 1
df['open'] = df['close'].shift(1)

# 매수가 계산
buy_price_tot = []
buy_time_tot = []
sell_price_tot = []
sell_time_tot = []

threshold_up = 10 #meaningless
threshold_down = -0.5 #meaningless

i = long
while i < df.shape[0]:
    # MA 역전 시 매수
    if df.iloc[i-1]['60>5']== False and df.iloc[i-2]['60>5']== True  : 
        buy_price_tot.append(df.iloc[i]['open'])
        buy_time_tot.append(df.iloc[i]['date'])

        for j in range(i,df.shape[0]-1) :        
            # QUICK OUT : threshold_up 넘는 강한 상승 보이면 탈출
            if df.iloc[j]['ror'] > threshold_up :                             
                sell_price_tot.append(df.iloc[j+1]['open'])
                sell_time_tot.append(df.iloc[j+1]['date'])
                break
            # 손절 : threshold_down 아래의 하방 보이면 손절
            elif df.iloc[j]['ror'] < threshold_down :                             
                sell_price_tot.append(df.iloc[j+1]['open'])
                sell_time_tot.append(df.iloc[j+1]['date'])
                break
            elif df.iloc[j]['60>5']== True :
                sell_price_tot.append(df.iloc[j+1]['open'])
                sell_time_tot.append(df.iloc[j+1]['date'])
                break
        i=j
    i += 1

# 데이터 결과 저장하기
ROR = pd.DataFrame([ x for x in zip(buy_time_tot,buy_price_tot,sell_time_tot,sell_price_tot)])
ROR.rename(columns={0:'buy_time', 1:'buy_price',2:'sell_time',3:'sell_price'}, inplace=True)

ROR['ror'] = ROR['sell_price']/ROR['buy_price'] - 0.005
ROR['cumror'] = ROR['ror'].cumprod()

print(ROR)

mdd_lst = [1]
i = 0
while i < ROR.shape[0]:
    mdd = 1
    if (ROR.iloc[i]['ror'] < 1):
        j = i
        while ROR.iloc[j]['ror'] < 1:
            mdd *= ROR.iloc[j]['ror']
            j += 1
            if j == ROR.shape[0]:
                break
        mdd_lst.append(mdd)
        i = j
    i += 1


print('{:,}'.format(round(ROR.iloc[-1]['cumror'],2)), long, short, threshold_down, min(mdd_lst))
filename = 'f{ticker}_simple_quickout_{threshold_up}_{threshold_down}_{long}_{short}_{start_date}_{end_date}_{date_type}.csv'   
file = open(filename, "w", encoding="utf-8-sig")  
ROR.to_csv('C:/finance_backtest/'+filename, index=None)




