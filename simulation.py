import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
import simpy as sp 

# read and create data frames for the csv files
RMIDF = pd.read_csv('rmi_inventory_level.csv')
CLSP = pd.read_csv('classifier_split.csv')
PFS = pd.read_csv('prefinish_statistics.csv')
PS = pd.read_csv('packaging_statistics.csv')

# store the data for the facilities in arrays
NAME = ['Detroit','Columbus','Springfield','Green Bay','Omaha']
NUM_OF_RMI_DRUMS = [40,30,50,20,30]
START_FROM = [0,40,70,120,140]
PREFINISH_EQUIPMENT = [2,3,1,2,3]
BAG_EQUIPMENT = [1,2,1,1,1]
CLASSIFIER_RATE = [3420,2280,1260,2050,4440]

def simulate(k):
    """
    Returns the time taken for a facility to complete its internal 
    work order
    
    Args:
        k (int): the index of the facility in the arrays that store 
        data

    Precondition: 
        k is an integer from 0 to 4 (inclusive)

    Returns: 
        float: time taken in hours (float)
    """
    print("Processing in " + NAME[k])

    # read the internal work order
    df = pd.read_csv(NAME[k]+'.csv')

    # create the RMI store
    rmi_store = [0]*40
    for i in range(NUM_OF_RMI_DRUMS[k]):
        i = i + START_FROM[k]
        if not pd.isna(RMIDF.iloc[i,3]):
            color_number = int(str(RMIDF.iloc[i,2])[14:])
            rmi_store[color_number-1] += int(RMIDF.iloc[i,3])
    
    # initialize the PFI store
    pfi_store = [0]*200
   
    # set up the simulation environment and resources
    env = sp.Environment()
    classifier = sp.Resource(env,1)
    prefinish = sp.Resource(env,PREFINISH_EQUIPMENT[k])
    bag_machine = sp.Resource(env,BAG_EQUIPMENT[k])
    box_machine = sp.Resource(env,1)

    def calculate_prefinish_rate(size,flavor):
        """ 
        Returns the processing rate for a prefinish operation by sampling 
        from a distribution that was fit to past data

        Args:
            size (int): size of the jellybeans processed in the prefinish 
            flavor (int): flavor of the jellybeans processed in the prefinish

        Precondition: 
            1. size ranges from 1 to 5 inclusive
            2. flavor ranges from 1 to 12 inclusive

        Returns: 
            float: processing rate in pounds per hour
        """
        index = (size-1)*12 + flavor-1

        while not (str(PFS.iloc[index,1]) == NAME[k]):
            index += 60
        
        mean = PFS.iloc[index,4]
        sd = PFS.iloc[index,5]
        return float(np.random.normal(mean,sd))

    def calculate_packaging_rate(size,packaging_type):
        """ 
        Returns the processing rate for a packaging operation by sampling 
        from a distribution that was fit to past data

        Args:
            size (int): size of the jellybeans processed in the prefinish
            packaging_type (str): flavor of the jellybeans processed in the 
            prefinish

        Precondition: 
            1. size ranges from 1 to 5 inclusive
            2. packaging_type is a str of the form 'Bag' or 'Box'

        Returns: 
            float: processing rate in pounds per hour
        """
        packaging_number = 1 if packaging_type=='Bag' else 0
        index = packaging_number + (size-1)*2

        while not (str(PS.iloc[index,1]) == NAME[k]):
            index += 10

        mean = PS.iloc[index,4]
        sd = PS.iloc[index,5]
        return float(np.random.normal(mean,sd)) 

    def find_pit(color,size):
        """ 
        Returns the index of the drum in prefinish store

        Args:
            color (int): color of the jellybeans whose drum is to be found
            size (int): size of the jellybeans whose drum is to be found

        Precondition:
            1. color ranges from 1 to 40 inclusive
            2. size ranges from 1 to 5 inclusive

        Returns: 
            int: index of the drum with the given color and size (integer)
        """
        return (color-1)*5 + size-1

    def amount_to_remove(color,size,quantity):
        """ 
        Returns the amount of jellybeans to remove from RMI based on the 
        classifier split

        Args:
            color (int): color of the jellybeans that have to be removed
            size (int): size of the jellybeans that have to be removed
            quantity (float): quantity (in pounds) of the jellybeans that 
            will go in the prefinish
        
        Precondition:
            1. color ranges from 1 to 40 inclusive
            2. size ranges from 1 to 5 inclusive
        
        Returns: 
            float: pounds of jellybeans to be emptied from the RMI
        """
        amount_existing = pfi_store[find_pit(color,size)]
        quantity_to_remove = (quantity-amount_existing) if amount_existing <= quantity else 0
        percentage = find_percentage(color,size)
        return (quantity_to_remove * 100)/percentage 
        
    def find_percentage(color,size):
        """ 
        Returns the percentage split in the classifier of the given size for
        the given color

        Args:
            color (int): color of the jellybeans that are to be split
            size (int): the size whose percentage is to be found
        
        Preconditions:
            1. color ranges from 1 to 40 inclusive
            2. size ranges from 1 to 5 inclusive

        Returns: 
            int: percentage split of the size
        """
        index = (color-1)*5
        while not (int(str(CLSP.iloc[index,1])[1:])==size):
            index += 1

        return int(CLSP.iloc[index,2])

    def fill_the_drums(color,size,amount):
        """ 
        Fills the drum for the given size and color in the prefinish store by the 
        given amount

        Args:
            color (int): color of the jellybeans that are filled
            size (int): size of the jellybeans that are filled
            amount (float): amount of jellybeans (in pounds) that are filled
        
        Preconditions:
            1. color ranges from 1 to 40 inclusive
            2. size ranges from 1 to 5 inclusive
        """

        pfi_store[find_pit(color,size)] += amount*find_percentage(color,size)*0.01
        for i in range(1,6):
            if i != size:
                pfi_store[find_pit(color,i)] += amount*find_percentage(color,i)*0.01

    def flow(info):
        """ 
        Simulates the flow of each instance in the internal work order

        Arg: 
            info: a row of the internal work order data frame. 
        
        Precondition: 
            The row has columns in the order of plant ID, internal work order ID, 
            color, size, flavor, packaging type, and quantity of that particular order
        """

        # setting up the information of the work order
        ID = info.iloc[1]
        color = int(str(info.iloc[2])[14:])
        size = int(str(info.iloc[3])[1:])
        flavor = int(str(info.iloc[4])[1:])
        packaging_type = str(info.iloc[5])
        quantity_in_pounds = float(info.iloc[6])

        # using the classifier machine
        with classifier.request() as classifier_req:
            yield classifier_req
            amount = amount_to_remove(color,size,quantity_in_pounds)
            rmi_store[color-1] -= amount
            fill_the_drums(color,size,amount)
            yield env.timeout(amount/CLASSIFIER_RATE[k])

        # using one of the pre-finish operation machines
        with prefinish.request() as prefinish_req:
            yield prefinish_req
            pfi_store[find_pit(color,size)] -= quantity_in_pounds
            prefinish_rate = calculate_prefinish_rate(size,flavor)
            yield env.timeout(quantity_in_pounds/prefinish_rate)

        # using one of the packaging machines 
        if packaging_type=='Bag':
            with bag_machine.request() as bag_machine_req:
                yield bag_machine_req
                bag_packaging_rate = calculate_packaging_rate(size,packaging_type)
                yield env.timeout(quantity_in_pounds/bag_packaging_rate)
        else:
            with box_machine.request() as box_machine_req:
                yield box_machine_req
                box_packaging_rate = calculate_packaging_rate(size,packaging_type)
                yield env.timeout(quantity_in_pounds/box_packaging_rate)

    # adds the process of simulating each work order to the environment
    (rows,cols) = df.shape
    for i in range(rows):
        env.process(flow(df.iloc[i]))

    # runs the processes and returns the time taken
    env.run()
    return env.now

simulations = [simulate(0),simulate(1),simulate(2),simulate(3),simulate(4)]
print(simulations)
