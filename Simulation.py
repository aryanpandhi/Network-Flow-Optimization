import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import simpy

# Reading and creating data frames for the csv files
RMIdf = pd.read_csv('RMI Inventory Level.csv')
CLSP = pd.read_csv('Classifier Split.csv')
PFS = pd.read_csv('Pre-finishStatistics.csv')
PS = pd.read_csv('PackagingStatistics.csv')

# Detroit, Columbus, Springfield, Green Bay, Omaha
name = ['Detroit','Columbus','Springfield','Green Bay','Omaha']
numOfRMIDrums = [40,30,50,20,30]
startFrom = [0,40,70,120,140]
RMICapacity = [300000,320000,88000,330000,440000]
prefinishEquipment = [2,3,1,2,3]
bagEquipment = [1,2,1,1,1]

def Simulate(k):
    # print(name[k])
    df = pd.read_csv(name[k]+str(2)+'.csv')

    RMI = [0]*40
    for i in range(numOfRMIDrums[k]):
        i = i + startFrom[k]
        if not pd.isna(RMIdf.iloc[i,3]):
            colorNumber = int(str(RMIdf.iloc[i,2])[14:])
            RMI[colorNumber-1] += int(RMIdf.iloc[i,3]) 
    
    # Creating the RMI Store for the manufacturing site
    # RMIStore = [None]*numOfRMIDrums[k]
    # for i in range(numOfRMIDrums[k]):
    #     j = i + startFrom[k]
    #     drum = str(RMIdf.iloc[j,1])
    #     color = str(RMIdf.iloc[j,2])
    #     capacity = RMICapacity[k]
    #     if pd.isna(RMIdf.iloc[j,3]):
    #         quantity = 0
    #     else:
    #         quantity = int(RMIdf.iloc[j,3])
    #     RMIStore[i]= st.RMIDrum(drum,color,quantity,capacity)

    PFIStore = [0]*200
   
    # Setting up the simulation environment and resources
    env = simpy.Environment()
    classifier = simpy.Resource(env,1)
    prefinish = simpy.Resource(env,prefinishEquipment[k])
    bagmachine = simpy.Resource(env,bagEquipment[k])
    boxmachine = simpy.Resource(env,1)

    # removes the required amount of jellybeans from the RMI drums
    # throws an exception if the drums do not contain enough of the beans
    
    def emptyTheDrums(color,amount):
        colorNumber = int(str(color)[14:])
        RMI[colorNumber-1] -= amount      
        # if round(RMI[colorNumber-1])<0 and amount!=0:
        #     print(color+str(RMI[colorNumber-1]))

    # determines the processing rate for PF operation using statistics from the past
    def calculateRatePF(size,flavor):
        ind = 60
        while not (PFS.iloc[ind,2]==size and PFS.iloc[ind,3]==flavor):
            ind+=1
        mean = PFS.iloc[ind,4]
        sd = PFS.iloc[ind,5]
        value = np.random.normal(mean,sd)
        return value

    # determines the processing rate for PA operstion using statistics
    def calculateRatePA(size,packagingtype):
        ind = 10 
        while not (PS.iloc[ind,2]==size and PS.iloc[ind,3]==packagingtype):
            ind += 1
        mean = PS.iloc[ind,4]
        sd = PS.iloc[ind,5]
        value = np.random.normal(mean,sd)
        return value 

    # converts the quantity from Stock Keeping Unit to Pounds
    def convertToPounds(quantity,packagingtype):
        if packagingtype == 'Bag':
            quantityinPounds = 0.25*quantity
        else:
            quantityinPounds = 2.5*quantity
        return quantityinPounds

    def findPit(color,size):
        colorNumber = (int(str(color)[14:])-1)*5
        sizeNumber = int(str(size)[1:])-1
        return colorNumber + sizeNumber

    # determines the amount of jellybeans to remove from RMI based on the classifier split
    def amountToRemove(color,size,quantity):
        index = findPit(color,size)
        amountExisting = PFIStore[index]
        if amountExisting <= quantity:
            # print(str(amountExisting)+ ' removed from store')
            quantity -= amountExisting
        else:
            # print(str(amount)+ ' removed from store')
            quantity = 0
        k = 0
        while not (CLSP.iloc[k,0]==color and CLSP.iloc[k,1]==size):
            k+=1
        percentage = int(CLSP.iloc[k,2])
        amount = (quantity * 100)/percentage 
        return amount
        
    # finds the percentage split in the classifier of the color and size
    def findPercentage(color,size):
        k = (int(str(color)[14:])-1)*5
        for i in range(5):
            j = i + k
            if CLSP.iloc[j,1]==size:
                return CLSP.iloc[j,2]

    def fillTheDrums(color,size,amount):
        PFIStore[findPit(color,size)] += amount*findPercentage(color,size)*0.01
        for i in range(5):
            j = i+1
            currSize = 'S'+str(j)
            if currSize != size:
                quantity = amount*findPercentage(color,currSize)*0.01
                index = findPit(color,currSize)
                PFIStore[index]+=quantity
                # print('filled '+str(quantity)+' of '+str(currSize)+' of '+str(color)+' in pos '+str(index))

    # Simulates the flow of each work order 
    def flow(info,CLResource,PFResource,BAResource,BOResource):

        # setting up the information of the work order
        ID = info.iloc[1]
        color = info.iloc[2]
        size = info.iloc[3]
        flavor = info.iloc[4]
        packagingtype = info.iloc[5]
        quantityInPounds = info.iloc[6]

        # using the classifier machine
        with CLResource.request() as req:
            yield req
            # print(str(ID) + " entered classifier at " + str(env.now))
            amount = amountToRemove(color,size,quantityInPounds)
            emptyTheDrums(color,amount)
            fillTheDrums(color,size,amount)
            PFIStore[findPit(color,size)]-=quantityInPounds
            # EXCEPTION IF OVERFILLED THE PFI DRUMS
            yield env.timeout(amount/2280)

        # using one of the pre-finish operation machines
        with PFResource.request() as req1:
            yield req1
            # print(str(ID) + " entered Pre-finish at " + str(env.now))
            processingTime = calculateRatePF(size,flavor)
            yield env.timeout(quantityInPounds/processingTime)

        # using one of the packaging machines 
        if packagingtype=='Bag':
            with BAResource.request() as req2:
                yield req2
                # print(str(ID) + " entered Packaging at " + str(env.now))
                processTime = calculateRatePA(size,packagingtype)
                yield env.timeout(quantityInPounds/processTime)
        else:
            with BOResource.request() as req3:
                yield req3
                # print(str(ID) + " entered Packaging at " + str(env.now))
                processTime = calculateRatePA(size,packagingtype)
                yield env.timeout(quantityInPounds/processTime)

    # adds the process of simulating each work order to the environment
    (rows,cols) = df.shape
    for i in range(rows):
        env.process(flow(df.iloc[i],classifier,prefinish,bagmachine,boxmachine))

    # runs the processes and prints the results
    env.run()
    return env.now

time = 0
# collecting = []
# xvalues = []
for i in range(20):     
    # xvalues = xvalues + [i]
    # print(i)
    simulations = [Simulate(0),Simulate(1),Simulate(2),Simulate(3),Simulate(4)]
    # if i==0:
    #     plt.bar([0,1,2,3,4],simulations)
    #     plt.title('Production Times')
    #     plt.xlabel('Iterations')
    #     plt.ylabel('Time (hours)')
    # #     plt.show()
    # collecting = collecting + [max(simulations)]
    time += max(simulations)

print(time/20)
