from pandas import read_csv, DataFrame 
from scipy.stats import norm
from scipy.stats import kstest

dfdata = read_csv('prefinish_data.csv')

collectlist = []
for k in range(0,300000,1000):
    param = norm.fit(dfdata.iloc[k:k+1000,3])
    test = kstest(dfdata.iloc[k:k+1000,3],'norm',args=param)
    collectlist.append([dfdata.iloc[k,0],dfdata.iloc[k,1],dfdata.iloc[k,2],param[0],param[1],test[1]])

df = DataFrame(collectlist,columns=['Site','Size','Flavor','Processing Mean','Processing SD','kstest - p'])

df.to_csv('prefinish_statistics.csv')

 