import numpy as np 
import pandas as pd 
import math

df = pd.read_csv('Order Bank.csv')
prefdf = pd.read_csv('Pre-finishStatistics.csv')
CLSP = pd.read_csv('Classifier Split.csv')
RMIdf = pd.read_csv('RMI Inventory Level.csv')

(rows,cols) = df.shape

# Detroit, Columbus, Green Bay, Springfield, Omaha
names = ['Detroit','Columbus','Green Bay', 'Springfield', 'Omaha']
classifierTimes = [3420, 2280, 2050, 1260, 4440]
numberOfPreFinish = [2,3,1,2,3]
numberOfBagMachines = [1,2,1,1,1]
numberOfBoxMachines = 1
prefinishTimes = [0]*5

numOfRMIDrums = [40,30,50,20,30]
startFrom = [0,40,70,120,140]

def findPercentage(color,size):
    k = (color-1)*5
    for i in range(5):
        j = i + k
        if CLSP.iloc[j,1]=='S'+str(size):
            return CLSP.iloc[j,2]

def RMIAtLocation(k):
    amount = [0]*40
    for i in range(numOfRMIDrums[k]):
        i = i + startFrom[k]
        if not pd.isna(RMIdf.iloc[i,3]):
            colorNumber = int(str(RMIdf.iloc[i,2])[14:])
            amount[colorNumber-1] += int(RMIdf.iloc[i,3])
    RMI = [0]*200
    for i in range(40):
        for j in range(5):
            color = i + 1
            size = j + 1
            perc = findPercentage(color,size)
            RMI[i*5+j] = amount[i]*perc*0.01
    return RMI

RMIAmounts1 = [RMIAtLocation(0),RMIAtLocation(1),RMIAtLocation(2),RMIAtLocation(3),RMIAtLocation(4)]
RMIAmounts2 = [RMIAtLocation(0),RMIAtLocation(1),RMIAtLocation(2),RMIAtLocation(3),RMIAtLocation(4)]

# print(RMIAmounts1[0][38*5:(38*5+5)])

# sums = 0
# for i in range(5):
#     sums+=RMIAmounts1[i][10+2]
# print('AMOUNT AVAILABLE IS '+str(sums))
# print('PERCENTAGE IS '+str(findPercentage(3,3)))

k = 0
for i in range(0,300,60):
    sumi = 0
    for j in range(60):
        row = i+j
        sumi += float(prefdf.iloc[row,4])
    prefinishTimes[k] = sumi/60
    k += 1

# Detroit, Columbus, Green Bay, Springfield, Omaha
boxTime = np.array([3416.8266,2741.8424,2049.139,1366.6054,4099.8748])
bagTime = np.array([2665.927,2127.123,1589.7858,1056.6812,3184.7034])

meanPackagingTime1 = np.true_divide(np.add(boxTime,bagTime),2)
meanPackagingTime1[1] = bagTime[1]+0.5*boxTime[1]
meanPackagingTime2 = np.true_divide(np.add(boxTime,bagTime),2)


colorAmount = [0]*200
amountCollection1 = [[0]*200 for _ in range(5)]
amountCollection2 = [[0]*200 for _ in range(5)]

workOrderTotal1 = []
workOrderTotal2 = []
for i in range(5):
    workOrderTotal1 += [[[0]*200 for _ in range(24)]]
    workOrderTotal2 += [[[0]*200 for _ in range(24)]]
# workOrderTotal1[0][1][2]=1
# print(workOrderTotal1[0][1])



# detroitTotal = [[0]*200 for _ in range(24)]
# columbusTotal = [[0]*200 for _ in range(24)]
# greenbayTotal = [[0]*200 for _ in range(24)]
# springfieldTotal = [[0]*200 for _ in range(24)]
# omahaTotal = [[0]*200 for _ in range(24)]
# workOrderTotal = [detroitTotal,columbusTotal,greenbayTotal,springfieldTotal,omahaTotal]

orderBankTotal = [[0]*200 for _ in range(24)]
totalTime1 = [0,0,0,0,0]
totalTime2 = [0,0,0,0,0]

def convertToPounds(quantity,packagingtype):
        if packagingtype == 'Bag':
            quantityinPounds = 0.25*quantity
        else:
            quantityinPounds = 2.5*quantity
        return quantityinPounds

for i in range(rows):
    colorNumber = (int(str(df.iloc[i,1])[11:])-1)*5
    sizeNumber = int(str(df.iloc[i,2])[1:])-1
    flavorNumber = (int(str(df.iloc[i,3])[1:])-1)*2
    if str(df.iloc[i,4]) == 'Bag':
        packagingNumber = 0
    else: 
        packagingNumber = 1
    colindex = colorNumber + sizeNumber
    rowindex = flavorNumber + packagingNumber
    colorAmount[colindex] += convertToPounds(int(df.iloc[i,5]),str(df.iloc[i,4]))   
    orderBankTotal[rowindex][colindex] += convertToPounds(int(df.iloc[i,5]),str(df.iloc[i,4])) 

# print(colorAmount)    
def determineAmount(color,size,quantity):
    k = 0
    color = 'Coloring Agent'+str(color)
    size = 'S'+str(size)
    while not (CLSP.iloc[k,0]==color and CLSP.iloc[k,1]==size):
        k+=1
    percentage = int(CLSP.iloc[k,2])
    amount = (quantity * 100)/percentage 
    return amount

# 1 accounts for no.of machines, 2 does not
def time(color,size,quantity,type):
    timeArray = [0]*5
    amount = determineAmount(color,size,quantity)
    for i in range(5):
        classifierTime = amount/classifierTimes[i]
        if type==1:
            prefinishTime = quantity/(prefinishTimes[i]*numberOfPreFinish[i])
            packingTime = quantity/(meanPackagingTime1[i])
        else:
            prefinishTime = quantity/prefinishTimes[i]
            packingTime = quantity/meanPackagingTime2[i]
        timeArray[i] = classifierTime+prefinishTime+packingTime
    return timeArray

collectlist = []
for i in range(200):
    color = int(i/5)+1
    size = i%5+1
    t1 = time(color,size,colorAmount[i],1)
    t2 = time(color,size,colorAmount[i],2)
    collectlist.append([color,size,colorAmount[i],t1[0],t2[0],t1[1],t2[1],t1[2],t2[2],t1[3],t2[3],t1[4],t2[4]])

obdf = pd.DataFrame(collectlist,columns=['Color','Size','Amount','D1','D2','C1','C2','G1','G2','S1','S2','O1','O2'],)

def findTotal(sizeAmounts,percentages):
    totals = [0]*5
    for i in range(5):
        if sizeAmounts[i] != None:
            totals[i] = (sizeAmounts[i]/percentages[i])*100
        else:
            totals[i] = None
    minii = math.inf
    argmin = -1
    for i in range(5):
        if totals[i]!=None and totals[i] < minii:
            minii = totals[i]
            argmin = i
    return [minii,argmin+1]

def possibleFacilities(color,setAmounts):
    facilities1 = []
    facilities2 = []
    for i in range(5):
        possible1 = True
        possible2 = True
        for j in range(5):
            possible1 = possible1 and RMIAmounts1[i][(color-1)*5+j]>=setAmounts[j]
            possible2 = possible2 and RMIAmounts2[i][(color-1)*5+j]>=setAmounts[j]
        if possible1:
            facilities1 = facilities1 + [i]
        if possible2:
            facilities2 = facilities2 + [i]
    return [facilities1,facilities2]
        
def dividingFacilities(color,setAmounts,type):
    facilities1 = []
    facilities2 = []
    if type == 1:
        for i in range(5):
            useful = False
            for j in range(5):
                useful = useful or RMIAmounts1[i][(color-1)*5+j]>0
            if useful: 
                facilities1 = facilities1 + [i]
        return facilities1
    else:
        for i in range(5):
            useful = False
            for j in range(5):
                useful = useful or RMIAmounts2[i][(color-1)*5+j]>0
            if useful: 
                facilities2 = facilities2 + [i]
        return facilities2

def findFacilities(color,setAmounts,facilities,type):
    if type ==1:
        maxes = [0]*5
        times= [0]*5
        for i in range(5):
            ind = 2*i + 3
            time = 0
            for j in range(5):
                k = j + (color-1)*5
                time += (setAmounts[j]/obdf.iloc[k,2])*obdf.iloc[k,ind]
            totalTime1[i] += time
            times[i] = time
            maxes[i] = np.amax(totalTime1)
            totalTime1[i] -= time
        min1 = maxes[facilities[0]]
        fac = facilities[0]
        for i in facilities:
            if maxes[i]<min1:
                min1 = maxes[i]
                fac = i
        return [fac,times[fac]]
    else:
        maxes = [0]*5
        times= [0]*5
        for i in range(5):
            ind = 2*i + 4
            time = 0
            for j in range(5):
                k = j + (color-1)*5
                time += (setAmounts[j]/obdf.iloc[k,2])*obdf.iloc[k,ind]
            totalTime2[i] += time
            times[i] = time
            maxes[i] = np.amax(totalTime2)
            totalTime2[i] -= time
        min2 = maxes[facilities[0]]
        fac = facilities[0]
        for i in facilities:
            if maxes[i]<min2:
                min2 = maxes[i]
                fac = i
        return [fac,times[fac]]

def timeFacilities(color,setAmounts,type):
    times1 = [None]*5
    times2 = [None]*5
    if type == 1:
        for i in range(5):
            ind1 = 2*i+3
            time1 = 0
            for j in range(5):
                k = j + (color-1)*5
                time1 += (min(setAmounts[j],RMIAmounts1[i][k])/obdf.iloc[k,2])*obdf.iloc[k,ind1]
            if time1>0:
                times1[i] = time1
        return times1
    else:
        for i in range(5):
            ind2 = 2*i+4
            time2 = 0
            for j in range(5):
                k = j + (color-1)*5
                time2 += (min(setAmounts[j],RMIAmounts2[i][k])/obdf.iloc[k,2])*obdf.iloc[k,ind2]
            if time2>0:
                times2[i] = time2
        return times2

def updateTimes(times,setAmounts,color,type):
    if type == 1:
        for i in range(5):
            if times[i] is not None:
                ind1 = 2*i+3
                time1 = 0
                for j in range(5):
                    k = j + (color-1)*5
                    time1 += (min(setAmounts[j],RMIAmounts1[i][k])/obdf.iloc[k,2])*obdf.iloc[k,ind1]
                times[i] = time1
        return times
    else:
        for i in range(5):
            if times[i] is not None:
                ind1 = 2*i+4
                time1 = 0
                for j in range(5):
                    k = j + (color-1)*5
                    time1 += (min(setAmounts[j],RMIAmounts1[i][k])/obdf.iloc[k,2])*obdf.iloc[k,ind1]
                times[i] = time1
        return times

def numberExists(arr):
    for i in range(len(arr)):
        if arr[i] != None:
            return True
    return False

def bestNonNone(times, type):
    mini = math.inf
    ind = -1
    if type == 1:
        for i in range(len(times)):
            if not (times[i] is None):
                totalTime1[i] += times[i]
                if np.amax(totalTime1) < mini:
                    mini = np.amax(totalTime1)
                    ind = i
                totalTime1[i] -= times[i]
    else:
        for i in range(len(times)):
            if not (times[i] is None):
                totalTime2[i] += times[i]
                if np.amax(totalTime2) < mini:
                    mini = np.amax(totalTime2)
                    ind = i
                totalTime2[i] -= times[i]
    assert ind != -1
    return ind

def smallerDistribution(times,setAmounts,color,type):
    totalAmount = np.sum(setAmounts)
    # print('initial amounts:')
    # print(setAmounts)
    # print('initial times:')
    # print(times)
    if type == 1:
        while numberExists(times) and round(totalAmount)>0:
            fac = bestNonNone(times,1)
            for i in range(5):
                toRemove = min(setAmounts[i],RMIAmounts1[fac][(color-1)*5+i])
                RMIAmounts1[fac][(color-1)*5+i] -= toRemove
                setAmounts[i] -= toRemove
                amountCollection1[fac][(color-1)*5+i] += toRemove
            totalAmount = np.sum(setAmounts)
            totalTime1[fac] += times[fac]
            times[fac] = None
            times = updateTimes(times,setAmounts,color,1)
            # print(setAmounts)
            # availableAmount = RMIAmounts1[fac][(color-1)*5+size-1]
            # if availableAmount>totalAmount:
            #     RMIAmounts1[fac][(color-1)*5+size-1] -= totalAmount
            #     totalTime1[fac] += times[fac]*(totalAmount/amount)
            #     totalAmount = 0
            #     for j in range(5):
            #         amountCollection1[fac][(color-1)*5+j] += setAmounts[j]
            # else:
            #     fract = availableAmount/totalAmount
            #     RMIAmounts1[fac][(color-1)*5+size-1] = 0
            #     totalTime1[fac] += times[fac]*(availableAmount/amount)
            #     for j in range(5):
            #         amt = setAmounts[j]*fract
            #         amountCollection1[fac][(color-1)*5+j] += amt 
            #         setAmounts[j] -= amt 
            #     totalAmount -= totalAmount*fract
            
        assert round(totalAmount)==0
    else:
        while numberExists(times) and round(totalAmount)>0:
            fac = bestNonNone(times,2)
            for i in range(5):
                toRemove = min(setAmounts[i],RMIAmounts2[fac][(color-1)*5+i])
                RMIAmounts2[fac][(color-1)*5+i] -= toRemove
                setAmounts[i] -= toRemove
                amountCollection2[fac][(color-1)*5+i] += toRemove
            totalAmount = np.sum(setAmounts)
            totalTime2[fac] += times[fac]
            times[fac] = None
            updateTimes(times,setAmounts,color,2)
            # print(setAmounts)
        # print(setAmounts)
        # print(RMIAmounts2[fac][(color-1)*5])
        # print(RMIAmounts2[0][(color-1)*5])
        # print(RMIAmounts2[1][(color-1)*5])
        # print(RMIAmounts2[2][(color-1)*5])
        # print(RMIAmounts2[3][(color-1)*5])
        assert round(totalAmount)==0

def distribute(total,size,color,amounts,percents):
    # print('distributing color '+str(color)+' and size '+str(size))
    setAmounts1 = [0]*5
    setAmounts2 = [0]*5
    for i in range(5):
        if amounts[i] != None:
            toRemove = percents[i]*total*0.01
            amounts[i] = amounts[i]-toRemove
            setAmounts1[i] = toRemove
            setAmounts2[i] = toRemove
    assert int(amounts[size-1])==0
    amounts[size-1] = None
    percent = percents[size-1]
    percents[size-1] = None
    for i in range(5):
        if percents[i] != None:
            percents[i] += (percents[i]/(100-percent))*percent
    [facilities1,facilities2] = possibleFacilities(color,setAmounts1)
    if len(facilities1) == 0:
        # print('smaller distribution 1')
        # posFacilities1 = dividingFacilities(color,setAmounts1,1)
        times1 = timeFacilities(color,setAmounts1,1)
        smallerDistribution(times1,setAmounts1,color,1)
    else:
        # print('larger distribution 1')
        [fac1,time1] = findFacilities(color,setAmounts1,facilities1,1)
        totalTime1[fac1] += time1
        num = (color-1)*5
        for i in range(5):
            RMIAmounts1[fac1][(color-1)*5+i] -= setAmounts1[i]
            amountCollection1[fac1][num+i] += setAmounts1[i]
    if len(facilities2)==0:
        # print('smaller distribution 2')
        # posFacilities2 = dividingFacilities(color,setAmounts2,2)
        times2 = timeFacilities(color,setAmounts2,2)
        smallerDistribution(times2,setAmounts2,color,2)
    else:
        # print('larger distribution 2')
        [fac2,time2] = findFacilities(color,setAmounts2,facilities2,2)
        totalTime2[fac2] += time2
        num = (color-1)*5
        # print('row num is' + str(fac1))
        for i in range(5):
            RMIAmounts2[fac2][(color-1)*5+i] -= setAmounts2[i]
            amountCollection2[fac2][num+i] += setAmounts2[i]
    return [amounts,percents]

def distributeColor(color,sizeAmounts,percentages):
    amounts = sizeAmounts
    percents = percentages
    for i in range(5):
        [total,size] = findTotal(amounts,percents)
        [amounts,percents] = distribute(total,size,color,amounts,percents)
    for i in range(5):
        assert amounts[i]==None

def divideTotalOrder():
    for i in range(0,200,5):
        sizeAmounts = [0]*5
        percentages = [0]*5
        for j in range(5):
            index = i+j
            sizeAmounts[j] = obdf.iloc[index,2]
            percentages[j] = CLSP.iloc[index,2]
        distributeColor(int(i/5)+1,sizeAmounts,percentages)
        
divideTotalOrder()
# # print(orderBankTotal)
# print(amountCollection1[2])

def distributeVector(i,j,amount): 
    amount1 = amount
    amount2 = amount
    for k in range(5):
        if amountCollection1[k][j] >= amount1:
            workOrderTotal1[k][i][j] += amount1
            amountCollection1[k][j] -= amount1
            amount1 = 0
        else:
            workOrderTotal1[k][i][j] += amountCollection1[k][j]
            amount1 -= amountCollection1[k][j]
            amountCollection1[k][j] = 0
    for k in range(5):
        if amountCollection2[k][j] >= amount2:
            workOrderTotal2[k][i][j] += amount2
            amountCollection2[k][j] -= amount2
            amount2 = 0
        else:
            workOrderTotal2[k][i][j] += amountCollection2[k][j]
            amount2 -= amountCollection2[k][j]
            amountCollection2[k][j] = 0

def assignFlavorAndPackage():
    for j in range(200):
        for i in range(24):
            distributeVector(i,j,orderBankTotal[i][j])

assignFlavorAndPackage()

def bagArrays(fac):
    order1 = workOrderTotal1[fac]
    order2 = workOrderTotal2[fac]
    bagArray1 = []
    bagArray2 = []
    for j in range(200):
        for i in range(0,24,2):
            color = int(j/5)+1
            size = j%5+1
            flavor = int(i/2)+1
            if order1[i][j]>0:
                bagArray1 += [[color,size,flavor,'Bag',order1[i][j]]]
            if order2[i][j]>0:
                bagArray2 += [[color,size,flavor,'Bag',order2[i][j]]]
    return [bagArray1,bagArray2]

def boxArrays(fac):
    order1 = workOrderTotal1[fac]
    order2 = workOrderTotal2[fac]
    boxArray1 = []
    boxArray2 = []
    for j in range(200):
        for i in range(1,24,2):
            color = int(j/5)+1
            size = j%5+1
            flavor = int(i/2)+1
            if order1[i][j]>0:
                boxArray1 += [[color,size,flavor,'Box',order1[i][j]]]
            if order2[i][j]>0:
                boxArray2 += [[color,size,flavor,'Box',order2[i][j]]]
    return [boxArray1,boxArray2]

def sortedArrays(b1,b2):
    b1len = len(b1)
    b2len = len(b2)
    for i in range(b1len):
        j = i
        while(j>0 and b1[j][4]<b1[j-1][4]):
            temp = b1[j]
            b1[j] = b1[j-1]
            b1[j-1] = temp
            j -= 1
    for i in range(b2len):
        j = i
        while(j>0 and b2[j][4]<b2[j-1][4]):
            temp = b2[j]
            b2[j] = b2[j-1]
            b2[j-1] = temp
            j -= 1
    return [b1,b2]



    # int len = b.length;
    #     for(int i =0;i<len;i++){
    #         int j =i;
    #         while(j>0 && b[j]<b[j-1]){
    #             int temp = b[j];
    #             b[j] = b[j-1];
    #             b[j-1] = temp;
    #             j--;
    #         }
    #     }

def createDataFrames(bagArray,boxArray,fac):
    numOfBags = len(bagArray)
    numOfBoxes = len(boxArray)
    collectlist = []
    k = 0
    for i in range(numOfBags-1,-1,-1):
        collectlist.append([names[fac],k,'Coloring Agent'+str(bagArray[i][0]),'S'+str(bagArray[i][1]),'F'+str(bagArray[i][2]),bagArray[i][3],bagArray[i][4]])
        k += 1
    for i in range(numOfBoxes-1,-1,-1):
        collectlist.append([names[fac],k,'Coloring Agent'+str(boxArray[i][0]),'S'+str(boxArray[i][1]),'F'+str(boxArray[i][2]),boxArray[i][3],boxArray[i][4]])
        k += 1
    df = pd.DataFrame(collectlist,columns=['Plant Id','Internal Work Order Id','Color','Size','Flavor','Packaging Type','Qty'])
    return df

def finalInternalWorkOrders(fac):
    [bagArray1,bagArray2] = bagArrays(fac)
    [boxArray1,boxArray2] = boxArrays(fac)
    [bagArray1,bagArray2] = sortedArrays(bagArray1,bagArray2)
    [boxArray1,boxArray2] = sortedArrays(boxArray1,boxArray2)
    df1 = createDataFrames(bagArray1,boxArray1,fac)
    df2 = createDataFrames(bagArray2,boxArray2,fac)
    df1.to_csv(names[fac]+str(1)+'.csv',index=False)
    df2.to_csv(names[fac]+str(2)+'.csv',index=False)


# order = workOrderTotal1[0]
# suma = 0
# for i in range(13*5,13*5+5):
#     for j in range(24):
#         suma += order[j][i]
# print(suma)

for i in range(5):
    finalInternalWorkOrders(i)

# print(amountCollection1[0][(13*5):(13*5)+5])

# print(amountCollection1[3])
# print(workOrderTotal1[3])
# [b1,b2] = boxArrays(3)
# [b3,b4] = sortedArrays(b1,b2)
# print(b1)
# print(b2)
# [b3,b4] = boxArrays(0)
# print(len(b1))
# print(len(b3))



# diff = [0]*200
# for i in range(200):
#     colorsum = 0
#     for j in range(5):
#         colorsum += amountCollection1[j][i]
#     diff[i] = (colorAmount[i]-colorsum)
# print(diff)

# difff = [[0]*200 for _ in range(24)]
# for j in range(200):
#     for i in range(24):
#         sums = 0
#         for k in range(5):
#             sums += workOrderTotal1[k][i][j]
#         difff[i][j] = orderBankTotal[i][j]-sums
# print(difff)
# print(orderBankTotal)

# print(totalTime1)
# print(totalTime2)
# print(amountCollection1)
# print(amountCollection2)

# divideTotalOrder()
# obdf.to_csv('Total Order.csv')