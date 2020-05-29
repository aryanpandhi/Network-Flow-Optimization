import numpy as np 
import pandas as pd 
import math

# read and create data frames for the csv files
OB = pd.read_csv('order_bank.csv')
PFS = pd.read_csv('prefinish_statistics.csv')
PS = pd.read_csv('packaging_statistics.csv')
CLSP = pd.read_csv('classifier_split.csv')
RMIDF = pd.read_csv('rmi_inventory_level.csv')

# Detroit, Columbus, Green Bay, Springfield, Omaha
NAME = ['Detroit','Columbus','Green Bay', 'Springfield', 'Omaha']
RMI_DRUMS = [40,30,20,50,30]
START_FROM = [0,40,120,70,140]
CLASSIFIER_RATE = [3420, 2280, 2050, 1260, 4440]
PREFINISH_EQUIPMENT = [2,3,2,1,3]
BAG_EQUIPMENT = [1,2,1,1,1]
BOX_EQUIPMENT = [1,1,1,1,1]

# set up the prefinish rates for each facility 
PREFINISH_RATE = [0]*5
for i in range(0,300,60):
    total = 0
    for j in range(60):
        total += float(PFS.iloc[i+j,4])
    PREFINISH_RATE[int(i/60)] = total/60

# set up the packaging rates for each facility
PACKAGING_RATE = [0]*5
for i in range(0,50,10):
    total = 0
    for j in range(10):
            if i%10 == 1:
                total += 2*PS.iloc[i+j,4] if j%2==1 else PS.iloc[i+j,4]
            else:
                total += PS.iloc[i+j,4]
    PACKAGING_RATE[int(i/10)] = total/10

def find_percentage(color,size):
    index = (color-1)*5
    while not (int(str(CLSP.iloc[index,1])[1:])==size):
        index += 1
    return int(CLSP.iloc[index,2])

def rmi_only_color(k):
    rmi_store_color = [0]*40
    for i in range(START_FROM[k],START_FROM[k] + RMI_DRUMS[k]):
        if not pd.isna(RMIDF.iloc[i,3]):
            color_number = int(str(RMIDF.iloc[i,2])[14:])
            rmi_store_color[color_number-1] += int(RMIDF.iloc[i,3])
    return rmi_store_color

def rmi_color_size(rmi_store_color):
    rmi_store = [0]*200
    for i in range(40):
        for j in range(5):
            percentage = find_percentage(i+1,j+1)
            rmi_store[i*5+j] = rmi_store_color[i]*percentage*0.01
    return rmi_store

def setup_rmi():
    rmi_amount = []
    for k in range(5):
        rmi_store_color = rmi_only_color(k)
        rmi_store = rmi_color_size(rmi_store_color)
        rmi_amount += [rmi_store]
    return rmi_amount

# set up the quantities in the RMI store for each facility
rmi_amount = setup_rmi()

def convert_to_pounds(quantity,packaging_type):
    return 0.25*quantity if packaging_type=='Bag' else 2.5*quantity

# determine total demand for jellybeans
demand_color_size = [0]*200
demand_total = [[0]*200 for _ in range(24)]
(rows,cols) = OB.shape
for i in range(rows):
    color_number = (int(str(OB.iloc[i,1])[11:])-1)*5
    size_number = int(str(OB.iloc[i,2])[1:])-1
    col_index = color_number + size_number
    flavor_number = (int(str(OB.iloc[i,3])[1:])-1)*2
    packaging_number = 0 if str(OB.iloc[i,4]) == 'Bag' else 1
    row_index = flavor_number + packaging_number
    demand_color_size[col_index] += convert_to_pounds(int(OB.iloc[i,5]),str(OB.iloc[i,4]))   
    demand_total[row_index][col_index] += convert_to_pounds(int(OB.iloc[i,5]),str(OB.iloc[i,4])) 

# initialize array to store the amount assigned to facilities
collected_amount = [[0]*200 for _ in range(5)]

# initialize array to store the approximated total time
total_time = [0,0,0,0,0]

def determine_amount(color,size,quantity):
    percentage = find_percentage(color,size)
    return (quantity * 100)/percentage 

def approx_time(color,size,quantity):
    times = [0]*5
    amount = determine_amount(color,size,quantity)
    for i in range(5):
        classifier_time = amount/CLASSIFIER_RATE[i]
        prefinish_time = quantity/(PREFINISH_RATE[i]*PREFINISH_EQUIPMENT[i])
        packaging_time = quantity/(PACKAGING_RATE[i])
        times[i] = classifier_time+prefinish_time+packaging_time
    return times

# determines amount demanded and its time approximations for each facility
TA = [[0]*6 for _ in range(200)]
for i in range(40):
    for j in range(5):
        times = approx_time(i+1,j+1,demand_color_size[i*5+j])
        TA[i*5+j] = [demand_color_size[i*5+j]] + times

def select_facility(color,set_amounts,facilities):
    max_values = [0]*5
    time_values = [0]*5
    for i in range(5):
        time = 0
        for j in range(5):
            row = j + (color-1)*5
            time += (set_amounts[j]/TA[row][0])*TA[row][i + 1]
        time_values[i] = time
        total_time[i] += time
        max_values[i] = np.amax(total_time)
        total_time[i] -= time
    minimum = max_values[facilities[0]]
    selected_facility = facilities[0]
    for i in facilities:
        if max_values[i] < minimum:
            minimum = max_values[i]
            selected_facility = i
    return [selected_facility,time_values[selected_facility]]

def update_times(times,set_amounts,color):
    for i in range(5):
        if times[i] is not None:
            time = 0
            for j in range(5):
                k = j + (color-1)*5
                time += (min(set_amounts[j],rmi_amount[i][k])/TA[k][0])*TA[k][i+1]
            times[i] = time
    return times

def fastest_facility(times):
    minimum = math.inf
    index = -1
    for i in range(5):
        if times[i] is not None:
            total_time[i] += times[i]
            if np.amax(total_time) < minimum:
                minimum = np.amax(total_time)
                index = i
            total_time[i] -= times[i]
    assert index != -1
    return index

def facility_exists(times):
    for i in range(5):
        if times[i] != None:
            return True
    return False

def separated_distribution(times,set_amounts,color):
    total_amount = np.sum(set_amounts)
    while facility_exists(times) and round(total_amount)>0:
        facility = fastest_facility(times)
        for i in range(5):
            to_remove = min(set_amounts[i],rmi_amount[facility][(color-1)*5+i])
            rmi_amount[facility][(color-1)*5+i] -= to_remove
            set_amounts[i] -= to_remove
            collected_amount[facility][(color-1)*5+i] += to_remove
        total_amount = np.sum(set_amounts)
        total_time[facility] += times[facility]
        times[facility] = None
        times = update_times(times,set_amounts,color)           
    assert round(total_amount)==0

def facility_times(color,set_amounts):
    times = [None]*5
    for i in range(5):
        time = 0
        for j in range(5):
            k = j + (color-1)*5
            time += (min(set_amounts[j],rmi_amount[i][k])/TA[k][0])*TA[k][i+1]
        if time > 0:
            times[i] = time
    return times

def feasible_facilities(color,set_amounts):
    facilities = []
    for i in range(5):
        feasible = True
        for j in range(5):
            feasible = feasible and rmi_amount[i][(color-1)*5+j] >= set_amounts[j]
        if feasible:
            facilities = facilities + [i]
    return facilities

def distribute(total,size,color,size_amounts,percentages):
    set_amounts = [0]*5
    for i in range(5):
        if size_amounts[i] != None:
            to_remove = percentages[i]*total*0.01
            size_amounts[i] = size_amounts[i]-to_remove
            set_amounts[i] = to_remove
    assert int(size_amounts[size-1])==0
    
    size_amounts[size-1] = None
    percent = percentages[size-1]
    percentages[size-1] = None
    
    for i in range(5):
        if percentages[i] != None:
            percentages[i] = (percentages[i]/(100-percent))*100
    
    facilities = feasible_facilities(color,set_amounts)
    if len(facilities) == 0:
        times = facility_times(color,set_amounts)
        separated_distribution(times,set_amounts,color)
    else:
        [selected_facility,time] = select_facility(color,set_amounts,facilities)
        total_time[selected_facility] += time
        for i in range(5):
            rmi_amount[selected_facility][(color-1)*5+i] -= set_amounts[i]
            collected_amount[selected_facility][(color-1)*5+i] += set_amounts[i]
    return [size_amounts,percentages]

def find_smallest_total(size_amounts,percentages):
    totals = [0]*5
    for i in range(5):
        check = size_amounts[i] != None
        totals[i] = (size_amounts[i]/percentages[i])*100 if check else None
    
    smallest_total = math.inf
    index = -1
    for i in range(5):
        if totals[i] != None and totals[i] < smallest_total:
            smallest_total = totals[i]
            index = i
    
    return [smallest_total,index+1]

def distribute_color(color,size_amounts,percentages):
    for i in range(5):
        [total,size] = find_smallest_total(size_amounts,percentages)
        [size_amounts,percentages] = distribute(total,size,color,size_amounts,percentages)
    for i in range(5):
        assert size_amounts[i]==None

def distribute_total_order():
    for i in range(0,200,5):
        size_amounts = [0]*5
        percentages = [0]*5
        for j in range(5):
            size_amounts[j] = TA[i+j][0]
            percentages[j] = find_percentage(int(i/5)+1,j+1)
        distribute_color(int(i/5)+1,size_amounts,percentages)

# distributes total order in terms of color and size to facilities
distribute_total_order()

# initialize a 3-d array to store the distribution of total order
total_order = []
for i in range(5):
    total_order += [[[0]*200 for _ in range(24)]]

def assign_combination(i,j,amount):
    for k in range(5):
        if collected_amount[k][j] >= amount:
            total_order[k][i][j] += amount
            collected_amount[k][j] -= amount
            amount = 0
        else:
            total_order[k][i][j] += collected_amount[k][j]
            amount -= collected_amount[k][j]
            collected_amount[k][j] = 0

def assign_flavor_package():
    for j in range(200):
        for i in range(24):
            assign_combination(i,j,demand_total[i][j])

# assigns flavor and packaging type to distributed jellybeans
assign_flavor_package()

def bag_arrays(facility):
    order = total_order[facility]
    bag_array = []
    for j in range(200):
        for i in range(0,24,2):
            if order[i][j] > 0:
                bag_array += [[int(j/5)+1,j%5+1,int(i/2)+1,'Bag',order[i][j]]]
    return bag_array

def box_arrays(facility):
    order = total_order[facility]
    box_array = []
    for j in range(200):
        for i in range(1,24,2):
            if order[i][j]>0:
                box_array += [[int(j/5)+1,j%5+1,int(i/2)+1,'Box',order[i][j]]]
    return box_array

def sort_array(arr):
    for i in range(len(arr)):
        j = i
        while(j > 0 and arr[j][4] < arr[j-1][4]):
            temp = arr[j]
            arr[j] = arr[j-1]
            arr[j-1] = temp
            j -= 1
    return arr

def create_data_frames(bag_array,box_array,facility):
    collect_list = []
    for i in range(len(bag_array)-1,-1,-1):
        collect_list.append([bag_array[i][0],bag_array[i][1],bag_array[i][2],bag_array[i][3],bag_array[i][4]])
    for i in range(len(box_array)-1,-1,-1):
        collect_list.append([box_array[i][0],box_array[i][1],box_array[i][2],box_array[i][3],box_array[i][4]])
    df = pd.DataFrame(collect_list,columns=['Color','Size','Flavor','Packaging Type','Quantity'])
    return df

def internal_work_orders(facility):
    bag_array = sort_array(bag_arrays(facility))
    box_array = sort_array(box_arrays(facility))
    df = create_data_frames(bag_array,box_array,facility)
    df.to_csv(NAME[facility]+'.csv',index=False)

# creates and outputs internal work orders for each facility
for i in range(5):
    internal_work_orders(i)
