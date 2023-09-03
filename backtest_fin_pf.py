import pandas as pd
import numpy as np

#################
# 1. Retrieving and preprocessing data
#################
'''
Symbol	    A005930
Symbol Name	삼성전자
Item	    6000906001
Item Name	영업이익(천원)
2000-01-31	9,060,339,619
'''
# retrieving with multi-column
df_tot = pd.read_excel("firm_data_prep.xlsx", header=[0, 1, 2], index_col=[0])
# df_tot.shape # 277 x 14048

# set format and name of index
df_tot.index = pd.to_datetime(df_tot.index)
df_tot.index.set_names('Month', inplace=True)

# return firm symbol col
df_tot.columns.get_level_values(0).unique()
# return variable col
df_tot.columns.get_level_values(2).unique()

###
# 1.2. Rename variables (troublesome due to multiindex already set)
###
'''
OP: operating profits
AT: total assets
P: closing price
MV: market value (capitalization)
'''
# Create a dict that match old name of var. and new name of that
dict_chg_var = dict({'영업이익(천원)':'OP', '총자산(천원)':'AT', '종가(원)':'P', '시가총액 (상장예정주식수 포함)(백만원)':'MV'})
# Get the MultiIndex as a list of tuples
multiindex_tuples = df_tot.columns.to_list()
# Replace the third element of each tuple with the new values
updated_multiindex_tuples = [(t[0], t[1], dict_chg_var[t[2]]) for t in multiindex_tuples]
# Convert the updated tuples back to a MultiIndex
new_multiindex = pd.MultiIndex.from_tuples(updated_multiindex_tuples, names=df_tot.columns.names)
# Assign the new MultiIndex to the DataFrame columns
df_tot.columns = new_multiindex

###
# 1.3. Separation by var.
###
# generate dataframe of OP
df_OP = df_tot.loc[:,df_tot.columns.get_level_values(2) == 'OP']
df_OP.columns = df_OP.columns.get_level_values(0) # use only first column (drop last two of three)
df_OP = df_OP.resample('Y').last() # convert time-frequency month to year 
# generate dataframe of AT
df_AT = df_tot.loc[:,df_tot.columns.get_level_values(2) == 'AT']
df_AT.columns = df_AT.columns.get_level_values(0)
df_AT = df_AT.resample('Y').last() # convert time-frequency month to year 

# generate dataframe of P
df_P = df_tot.loc[:,df_tot.columns.get_level_values(2) == 'P']
df_P.columns = df_P.columns.get_level_values(0)
# generate dataframe of MV
df_MV = df_tot.loc[:,df_tot.columns.get_level_values(2) == 'MV']
df_MV.columns = df_MV.columns.get_level_values(0)

###
# 1.4. Prepare dataframe contains sort variable (operating profits divided by assets)
###
# Divide operating profits by assets
df_OPtoAT = df_OP.div(df_AT)
# convert time-frequency month to year 
df_OPtoAT = df_OPtoAT.resample('Y').last()
# check between df_OPtoAT and df_OP/df_AT
for _ in range(10):
    i = np.random.randint(0,24)
    j = np.random.randint(0,1000)
    print(df_OP.resample('Y').last().iloc[i,j]/df_AT.iloc[i,j], '\t', df_OPtoAT.iloc[i,j])

#################
# 2. Backtesting
#################

###
# 2.1. 
###

## funcion ##
## def ##
# for y in df_OPtoAT.index:
#     df_OPtoAT_temp = df_OPtoAT.loc[y,:]
#     df_OPtoAT_temp = 

y = df_OPtoAT.index[0]
df_OPtoAT_temp = df_OPtoAT.loc[y,:].dropna().sort_values(ascending=False) # sorting by value

# set firm no.
no = 50

# select high scored firm
firm_sel = df_OPtoAT_temp.iloc[:no].index

# equal-weight
weight = 'equal' # 'value'
if weight == 'equal':

# position - long from Jul of year t+1 to Jun of year t+2
long_start = pd.Timestamp(y.year + 1, 6, 30) 
long_end = pd.Timestamp(y.year + 2, 6, 30) 

df_P.loc[long_start:long_end, ] 
'''
Problem. 상위 50개 기업 중 비상장기업이 있는 경우 50개가 되질 못함
A1. 넉넉하게 100개 기업으로 잡고 NaN이 아닌 기업에 대해서만 분석
A2. 각 월마다 price 값이 존재하는 기업 50개를 찾아서 분석
'''
###
# A2. 
###
i = 0
firm_sel_nonan = []
while len(firm_sel_nonan) < no:
    firm = df_OPtoAT_temp.index[i]
    # Jun of year t+2에 가격 데이터가 없는 기업은 제외
    if not(pd.isna(df_P.loc[long_start, firm])) and not(pd.isna(df_MV.loc[long_start, firm])) :
        firm_sel_nonan.append(firm)
    i += 1

###
#
###
df_P_temp = df_P.loc[long_start:long_end, firm_sel_nonan] # contain last mth
df_MV_temp = df_MV.loc[long_start:long_end, firm_sel_nonan]


df_OPtoAT_temp[firm_sel_nonan]

# select high scored firm
firm_sel = df_OPtoAT_temp.iloc[:no].index

