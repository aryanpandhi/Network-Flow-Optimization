import numpy as np 
import pandas as pd 
from scipy.stats import norm
from scipy.stats import kstest

dfdata = pd.read_csv('Pre-finish.csv')

collectlist = []
for k in range(0,300000,1000):
    param = norm.fit(dfdata.iloc[k:k+1000,3])
    test = kstest(dfdata.iloc[k:k+1000,3],'norm',args=param)
    collectlist.append([dfdata.iloc[k,0],dfdata.iloc[k,1],dfdata.iloc[k,2],param[0],param[1],test[1]])

df = pd.DataFrame(collectlist,columns=['Site','Size','Flavor','ProcessingMean','ProcessingSD','kstest-p'])
# print(df)
# df.info()

# df.to_csv('Pre-finishStatistics.csv')

print('min p is ' + str(min(df.iloc[:,5])))


# df2 = df[df.iloc[:,5]>0.05]
# df2.info()
 