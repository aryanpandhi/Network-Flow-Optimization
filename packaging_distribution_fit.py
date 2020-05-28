from pandas import read_csv, DataFrame
from scipy.stats import norm
from scipy.stats import kstest

dfdata = read_csv('packaging_data.csv')

collectlist = []
for k in range(0,50000,1000):
    param = norm.fit(dfdata.iloc[k:k+1000,3])
    test = kstest(dfdata.iloc[k:k+1000,3],'norm',args=param)
    collectlist.append([dfdata.iloc[k,0],dfdata.iloc[k,1],dfdata.iloc[k,2],param[0],param[1],test[1]])

df = DataFrame(collectlist,columns=['Site','Size','Packaging Type','Processing Mean','Processing SD','kstest - p'])

df.to_csv('packaging_statistics.csv')
