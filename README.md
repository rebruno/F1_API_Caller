# F1 API Caller
 Python code to work with Ergast's Motorrace Database

# How to use

There are 2 main ways to use this code: either by using the APIRequests to get raw data yourself(usually returned as a Numpy array or a Python list), or by using the functions already provided to compare laptimes, quali results, etc...

Recommended to put cache.install_cache() to cache API requests.


## Necessary Libraries

Libraries that need to be installed: matplotlib, numpy, requests_cache. They can all be installed through pip.

## APIRequests.py

This has a few functions to get data directly from the Motorrace database.
For example, to get laptimes for a certain race for a driver, you would use get_laps(season, round_number, driverID). Driver IDs can be found with get_id(name) where a search is performed. This would return an array of laptimes on success, or an empty array on failure(incorrect parameters or simply no laptimes available)

## driverCompare.py & driverPlots.py

There are a few functions already made to compare driver laptimes. For usage information, just check their help() response.

1. driverPlots.py
   * head_to_head_laptime(driverIDList, season, round_number, startLap = 0, endLap = None, laps = 0, cutoff=None)
   * driver_lap_boxplot(driverIDList, season, round_number, startLap=None, endLap=None, exclude=-1, scatter=True)

2. driverCompare.py
   * driver_lap_comparaison(driverIDList, season, round_number, n, percent = 1, startLap = None, endLap = None)
   * driver_lap_comparaison(driverIDList, season, round_number)

## methods.py

This contains functions required for the other modules to work. Most useful one that could be used independently is get_lap_stats which returns the laps and lap average of a driver at a certain Grand Prix. 
