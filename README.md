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
- **total_order.py**: generates work orders for each of the facilities by dividing up the total order effectively. outputs 5 files (**detroit.csv**, **columbus.csv**, **springfield.csv**, **green bay.csv**, **omaha.csv**) containing the work order for each of the 5 facilities.
- **simulation.py**: simulates the work order for each facility and prints the time taken by the facility to process the order

## Running Simulations
### Installing SimPy
SimPy is needed to run **simulation.py**. Use the package manager pip to install SimPy
```bash
pip install simpy
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Authors
Aryan Pandhi - [aryanpandhi](https://github.com/aryanpandhi)

## License
This project is licensed under the MIT License - see [LICENSE.txt](https://github.com/aryanpandhi/Network-Flow-Optimization/blob/master/LICENSE.txt) for details 
