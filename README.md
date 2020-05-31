# Network-Flow-Optimization

This project aims to create an algorithm that effectively distributes a production order received by a firm (to its manufacturing facilities), and create a simulation that measures how long the distributed production takes. The facilities have varying number of equipment with varying capabilities. The goal is to distribute the total order such that the entire production is over in a set amount of time. The detailed problem statement, algorithm design and result is reported in the file **network-flow-optimization.pdf**.

## Input Data
- **order_bank.csv**: contains the total order received by the firm
- **prefinish_data.csv**: contains past data on the processing rates of the prefinish equipment at each facility
- **packaging_data.csv**: contains past data on the processing rates of the packaging equipment at each facility

## Python Files
- **prefinish_distribution_fit.py**: fits the data from **prefinish_data.csv** to a gaussian distribution and runs the Kolmogorov Smirnov test on the fit. outputs the file **prefinish_statistics.csv** containing the statistics.
- **packaging_distribution_fit.py**: fits the data from **packaging_data.csv** to a gaussian distribution and runs the Kolmogorov Smirnov test on the fit. outputs the file **packaging_statistics.csv** containing the statistics.
- **constants.py**: module that contains constants for the scripts **total_order.py** and **simulation.py**
