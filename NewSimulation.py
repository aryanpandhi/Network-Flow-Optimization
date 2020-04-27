import numpy as np 
import pandas as pd 
import Storage as st
import simpy

# Reading and creating data frames for the csv files
codf = pd.read_csv('Workorder Example.csv')
RMIdf = pd.read_csv('RMI Inventory Level.csv')
PFIdf = pd.read_csv('Pre-finish Inventory Drum.csv')
PIdf = pd.read_csv('Pack Inventory Drum.csv')
CLSP = pd.read_csv('Classifier Split.csv')
PFS = pd.read_csv('Pre-finishStatistics.csv')
PS = pd.read_csv('Packaging_Statistics.csv')

freePFIDrums = 32
nextPFIDrumToEmpty = 0

# Creating the RMI Store for the manufacturing site
RMIStore = [None]*30
for i in range(30):
    j = i + 40
    drum = str(RMIdf.iloc[j,1])
    color = str(RMIdf.iloc[j,2])
    capacity = 320000
    if pd.isna(RMIdf.iloc[j,3]):
        quantity = 0
    else:
        quantity = int(RMIdf.iloc[j,3])
    RMIStore[i]= st.RMIDrum(drum,color,quantity,capacity)

# Creating the PFI Store for the manufacturing site
PFIStore = [None]*32
for i in range(32):
    j = i + 15
    drum = str(PFIdf.iloc[j,1])
    capacity = 3500*0.95
    PFIStore[i]= st.PFIDrum(drum,capacity)

# Creating the PI Store for the manufacturing site
PIStore = [None]*10
for i in range(10):
    j = i + 8
    drum = str(PIdf.iloc[j,1])
    capacity = 10000*0.95
    PIStore[i]= st.PIDrum(drum,capacity)

# Setting up the simulation environment and resources
env = simpy.Environment()
classifier = simpy.Resource(env,1)
prefinish = simpy.Resource(env,3)
bagmachine = simpy.Resource(env,2)
boxmachine = simpy.Resource(env,1)

# removes the required amount of jellybeans from the RMI drums
# throws an exception if the drums do not contain enough of the beans
def emptyRMIDrums(color,amount):
    i = 0
    emptied = False
    while i<30 and not emptied:
        if RMIStore[i].color==color:
            if RMIStore[i].quantity>=amount:
                #print(str(currentAmount) + ' removed from drum ' + str(i))
                RMIStore[i].quantity = RMIStore[i].quantity - amount
                amount = 0
                emptied = True
            else:
                #print('emptied drum ' + str(i))
                amount = amount - RMIStore[i].quantity
                RMIStore[i].quantity = 0        
        i+=1
    if amount != 0:
        raise Exception('No RMI Drum with enough quantity')

# determines the processing rate for PF operation using statistics from the past
def calculateRatePF(size,flavor):
    ind = 60
    while not (PFS.iloc[ind,2]==size and PFS.iloc[ind,3]==flavor):
        ind+=1
    mean = PFS.iloc[ind,4]
    sd = PFS.iloc[ind,5]
    value = np.random.normal(mean,sd)
    return value

# determines the processing rate for 
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

# determines the amount of jellybeans to remove from RMI based on the classifier split
def amountToRemove(color,size,quantity):
    k = 0
    while not (CLSP.iloc[k,0]==color and CLSP.iloc[k,1]==size):
        k+=1
    percentage = int(CLSP.iloc[k,2])
    return (quantity * 100)/percentage 

# determines if the beans can be filled in an already filled PFI drum
def remainingSpace(color,size,quantity):
    filled = 0
    for i in range(32):
        if PFIStore[i].color==color and PFIStore[i].size==size:
            filled += capacity-quantity
    if filled>quantity:
        return 1
    return 0

# finds the percentage split in the classifier of the color and size
def findPercentage(color,size):
    k = (int(str(color)[14:])-1)*5
    for i in range(5):
        j = i + k
        if CLSP.iloc[j,1]==size:
            return CLSP.iloc[j,2]

# determines whether there is enough space in the PFI storage
def availability(color,amount):
    if freePFIDrums >= 5:
        return True
    quantityForS1 = amount*findPercentage(color,'S1')/100
    quantityForS2 = amount*findPercentage(color,'S2')/100
    quantityForS3 = amount*findPercentage(color,'S3')/100
    quantityForS4 = amount*findPercentage(color,'S4')/100
    quantityForS5 = amount*findPercentage(color,'S5')/100
    spaceS1 = remainingSpace(color,'S1',quantityForS1)
    spaceS2 = remainingSpace(color,'S2',quantityForS2)
    spaceS3 = remainingSpace(color,'S3',quantityForS3)
    spaceS4 = remainingSpace(color,'S4',quantityForS4)
    spaceS5 = remainingSpace(color,'S5',quantityForS5)

    if spaceS1+spaceS2+spaceS3+spaceS4+spaceS5+freePFIDrums>=5:
        return True

    return False

def emptyPFIDrums(next):
    if next > 27:
        numToEmpty = 32 - next
        newToEmpty = 5 - numToEmpty
        for i in range(numToEmpty):
            i = i + next
            if PFIStore[i].color != None:
                sendForward(PFIStore[i].size,'F1',PFIStore[i].quantity)
                PFIStore[i].quantity=0
                PFIStore[i].color = None
                PFIStore[i].size = None
        for i in range(newToEmpty):
            if PFIStore[i].color != None:
                sendForward(PFIStore[i].size,'F1',PFIStore[i].quantity)
                PFIStore[i].quantity=0
                PFIStore[i].color = None
                PFIStore[i].size = None
        nextPFIDrumToEmpty = newToEmpty
    else: 
        for i in range(5):
            i = i + next
            if PFIStore[i].color != None:
                sendForward(PFIStore[i].size,'F1',PFIStore[i].quantity)
                PFIStore[i].quantity=0
                PFIStore[i].color = None
                PFIStore[i].size = None
        nextPFIDrumToEmpty += 5
    freePFIDrums += 5

def sendForward(size,flavor,quantity):
    with prefinish.request() as req4:
        yield req4
        processingTime = calculateRatePF(size,flavor)
        yield env.timeout(quantity/processingTime)
    with bagmachine.request() as req5:
        yield req5
        processTime = calculateRatePA(size,'Bag')
        yield env.timeout(quantity/processTime)
    
def findFirstEmptyPFIDrum():
    i=0
    while PFIStore[i].color != None:
        i+=1
    return i 

def fillPFIDrums(color,amount):
    quantityForS1 = amount*findPercentage(color,'S1')/100
    quantityForS2 = amount*findPercentage(color,'S2')/100
    quantityForS3 = amount*findPercentage(color,'S3')/100
    quantityForS4 = amount*findPercentage(color,'S4')/100
    quantityForS5 = amount*findPercentage(color,'S5')/100
    remaining = [0]*5
    remaining[0] = determineRemaining(color,'S1',quantityForS1)
    remaining[1] = determineRemaining(color,'S2',quantityForS2)
    remaining[2] = determineRemaining(color,'S3',quantityForS3)
    remaining[3] = determineRemaining(color,'S4',quantityForS4)
    remaining[4] = determineRemaining(color,'S5',quantityForS5)
    
    firstEmptyDrum = 
    for i in range(5):
        if remaining[i]>0:


    return None

def determineRemaining(color,size,quantity):
    toFill = quantity
    for i in range(32):
        if PFIStore[i].color==color and PFIStore[i].size==size:
            space = PFIStore[i].capacity - PFIStore[i].quantity
            if space>=toFill:
                PFIStore[i].quantity += toFill
                toFill = 0
                return toFill
            else: 
                PFIStore[i].quantity += space
                toFill -= space
    return toFill


# Simulates the flow of each work order 
def flow(info,CLResource,PFResource,BAResource,BOResource):

    # setting up the information of the work order
    ID = info.iloc[1]
    color = info.iloc[2]
    size = info.iloc[3]
    flavor = info.iloc[4]
    packagingtype = info.iloc[5]
    quantityInPounds = convertToPounds(info.iloc[6],packagingtype)

    # using the classifier machine
    with CLResource.request() as req:
        yield req
        amount = amountToRemove(color,size,quantityInPounds)
        if not availability(color,amount):
            emptyPFIDrums(nextPFIDrumToEmpty)
        
        print(str(ID) + " entered classifier at " + str(env.now))
        emptyRMIDrums(color,amount)
        yield env.timeout(amount/2280)
        fillPFIDrums(color,amount)
        

    # using one of the pre-finish operation machines
    with PFResource.request() as req1:
        yield req1
        print(str(ID) + " entered Pre-finish at " + str(env.now))
        processingTime = calculateRatePF(size,flavor)
        yield env.timeout(quantityInPounds/processingTime)

    # using one of the packaging machines 
    if packagingtype=='Bag':
        with BAResource.request() as req2:
            yield req2
            print(str(ID) + " entered Packaging at " + str(env.now))
            processTime = calculateRatePA(size,packagingtype)
            yield env.timeout(quantityInPounds/processTime)
    else:
        with BOResource.request() as req3:
            yield req3
            print(str(ID) + " entered Packaging at " + str(env.now))
            processTime = calculateRatePA(size,packagingtype)
            yield env.timeout(quantityInPounds/processTime)

# adds the process of simulating each work order to the environment
(rows,cols) = codf.shape
for i in range(rows):
    env.process(flow(codf.iloc[i],classifier,prefinish,bagmachine,boxmachine))

# runs the processes and prints the results
env.run()
print('Columbus simulation over after ' + str(env.now*60)+ ' min')
print('Columbus simulation over after ' + str(env.now)+ ' hours')
    