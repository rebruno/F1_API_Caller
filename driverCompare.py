import json
import requests as req
import requests_cache as cache
import numpy as np

from . import APIRequests
from . import constants
from .methods import *


def driver_lap_comparaison(driverIDList, season, round_number, n, percent = 1, startLap = None, endLap = None):
	"""
	Takes a list of driverIDs and compares the lap averages to the first entry.
	Season and round number determine which race is used.
	
	n and percent determine how many laps are used for comparing. It takes the n fastest laps or the top percent% laps,
	when all laps are sorted from fastest to slowest. 
	A higher n/percent would take the average over more laps, so the average race performance.
	A lower value would compare how fast 1 car is to another over a single lap.
	"""

	driverLapData = []
	driverGaps = []

	driver1Stats = get_lap_stats(driverIDList[0], season, round_number, n, percent, startLap = startLap, endLap = endLap)
	driverLapData.append(driver1Stats)
	laptime = driver1Stats[2]
	driverGaps.append((driverIDList[0], 0))

	for driverID in driverIDList[1:]:
		driverStats = get_lap_stats(driverID, season, round_number, n, percent, startLap = startLap, endLap = endLap)
		driverLapData.append(driver1Stats)
		driverGaps.append((driverID, driverStats[2]-laptime))


	return driverLapData, driverGaps




