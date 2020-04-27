import numpy as np 
import pandas as pd 

RMIdf = pd.read_csv('RMI Inventory Level.csv')
(rows,cols) = RMIdf.shape

location = ['Detroit','Columbus','Springfield','Green Bay','Omaha']
numOfRMIDrums = [40,30,50,20,30]
startFrom = [0,40,70,120,140]

def RMIAtLocation(k):
    amount = [0]*40
    for i in range(numOfRMIDrums[k]):
        i = i + startFrom[k]
        if not pd.isna(RMIdf.iloc[i,3]):
            colorNumber = int(str(RMIdf.iloc[i,2])[14:])
            amount[colorNumber-1] += int(RMIdf.iloc[i,3])

    collectlist = []
    for i in range(40):
        if amount[i]>0:
            collectlist.append([location[k],i+1,amount[i]])

    df = pd.DataFrame(collectlist,columns=['Site','Color','Amount'])
    return df

dfs = (RMIAtLocation(0),RMIAtLocation(1),RMIAtLocation(2),RMIAtLocation(3),RMIAtLocation(4))
dffinal = pd.concat(dfs,ignore_index=True)
dffinal.to_csv('RMITotal.csv')