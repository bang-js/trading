import pandas as pd
import numpy as np
from pykrx import stock
import datetime as dt

''' 시총 하위 20% 중 영업이익/자산 상위 50개 (reversal 무시)'''

# 영업이익/자산 순위 결정
# https://opendart.fss.or.kr/disclosureinfo/fnltt/cmpnyacnt/main.do
df = pd.read_excel('Account_22Q3.xlsx', engine='openpyxl')
df = df[df!='-조회결과없음-']
df = df[df!=' -표준계정코드<br/>미사용- ']
df = df[df!=0]
df.dropna(inplace=True)
df['name_pr']=df['회사명'].str.split("(").str[0]
df['영업이익'].astype('float')
df['OPtA']=df['영업이익']/df['자산총계']
df.sort_values(by='OPtA',ascending=False, inplace=True) #내림차순
df.reset_index(inplace=True, drop=True)

# 시가총액 순위 결정
# https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201 시총 등 
# https://data.krx.co.kr/contents/MDC/MDI/mdiLoader/index.cmd?menuId=MDC0201020201 주식종류 -> 위 파일에 합치기
df_2 =  pd.read_excel('market_2212.xlsx', engine='openpyxl' )
df_2 = df_2[df_2['소속부'] != '관리종목(소속부없음)'] 
df_2 = df_2[df_2['소속부'] != 'SPAC(소속부없음)'] 
df_2 = df_2[~df_2['시장구분'].str.contains("KONEX")]
df_2 = df_2[df_2['주식종류'] == '보통주'] 
df_2 = df_2[df_2['시가총액']> 10_000_000_000] #100억이상

df_2.sort_values(by='시가총액',ascending=True, inplace=True) #오름차순
df_2.reset_index(inplace=True, drop=True)

# 시총 하위 20%만 살리기
threshold = 0.2
names = df_2.loc[: df_2.shape[0] * threshold ,'종목명'].to_list()

df['overlap'] = False
for i in range(int(df.shape[0]/2)): # 전체탐색X 일부만
    if i%100 == 0: # 진행상황
        print(i/df.shape[0])
    for j in names: # df에서 찾은 회사명이 df_2의 종목명list에 있는 경우
        if j == df.loc[i,'name_pr']:
            df.loc[i, 'overlap'] = True
            
df = df[df['overlap']==True]
df.reset_index(inplace=True, drop=True)
cand = df['name_pr'].to_list()

# 전달대비 +7% 이하인 종목
base_date = dt.datetime.strptime('2022-12-27', '%Y-%m-%d')  # dt.datetime.now()   

rev = [] # 살릴 종목 저장
# 종목코드 가져오기
df_2['종목코드'] = df_2['종목코드'].astype(str).str.zfill(6) 
ticker_dict = dict(zip(df_2['종목명'].to_list(),df_2['종목코드'].to_list())) # {종목명:종목코드} 종목명이 key
for c in cand:
    ticker = ticker_dict.get(c)
    df_temp = stock.get_market_ohlcv(base_date - dt.timedelta(days=30), base_date, ticker,'d')
    #df_temp = stock.get_market_ohlcv('20220701','20220731', ticker,'d')
    try:
        ror = df_temp.iloc[-1]['종가']/df_temp.iloc[0]['종가']
        if ror < 1.07 : # 전달 대비 7% 미만 상승 종목
            rev.append(c)
    except:
        continue

df['rev'] = False
for i in range(int(df.shape[0])):
    if i%100 == 0:
        print(i/df.shape[0])
    for l in rev:
        if l in df.iloc[i]['name_pr']:
            df.loc[i,'rev'] = True
            break

# df = df[df['rev']==True]
df.reset_index(inplace=True, drop=True)

# 자산 수
no_asset = 50
cand = df.loc[:no_asset-1,'name_pr'].to_list()
        
# 최종
print(len(cand), cand)

# 점검
k=[]
for c in cand:
    if not(c in names):
        print('not')

