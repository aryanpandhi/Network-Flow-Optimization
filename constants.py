"""
This module contains constants for the scripts that create 
internal work orders (total_order.py) and simulate (simulation.py)
the work orders.

Author: Aryan Pandhi
Date: May 30, 2020 (Python 3 Version)
"""
from pandas import read_csv

# read and create data frames for the csv files
OB = read_csv('order_bank.csv')
RMIDF = read_csv('rmi_inventory_level.csv')
CLSP = read_csv('classifier_split.csv')
PFS = read_csv('prefinish_statistics.csv')
PS = read_csv('packaging_statistics.csv')

# store the data for the facilities in arrays
NAME = ['Detroit','Columbus','Green Bay','Springfield','Omaha']
RMI_DRUMS = [40,30,20,50,30]
START_FROM = [0,40,120,70,140]
CLASSIFIER_RATE = [3420,2280,2050,1260,4440]
PREFINISH_EQUIPMENT = [2,3,2,1,3]
BAG_EQUIPMENT = [1,2,1,1,1]