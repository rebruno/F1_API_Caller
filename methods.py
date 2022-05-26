import json
import requests as req
import requests_cache as cache
import numpy as np

from . import APIRequests
from . import constants



def get_sec(times):
	try:
		m,s = times.split(":")
	except ValueError:
		return 0
	return round(int(m)*60 + float(s), 4)

def getPtsSystem(season, drivers, ptsSystem):
	"""
	This function returns the points a driver would have in an alternate point system. 
	Useful if you want to compare what a driver from today would have from an earlier point system,
	or what a driver from before 2010 would have with the current system(doesn't account for sprint races or fastest lap points).
	"""
	driverPts = {}
	for driver in drivers: 
		driverPts[driver] = []
		pts = 0
		for race in driver.raceResults[season].keys():
			driverPts[driver].append(ptsSystem[driver.raceResults[season][race]])
			pts += ptsSystem[driver.raceResults[season][race]]
	print(driver.driverID, season, pts)
	return driverPts

def rolling_average(lapTimes, n=3):
	return np.convolve(lapTimes, np.ones(n), 'valid')/n

def rolling_laptimes(driverID, season, round_number, laps = 3, startLap = None, endLap = None):

	driverLaps = APIRequests.get_laps(season, round_number, driverID)
	if len(driverLaps) <= 0:
		return None

	rollingMeanLaptime = rolling_average(driverLaps[startLap:endLap], n=laps)
	return rollingMeanLaptime	


def get_lap_stats(driverID, season, round_number, n, percent = 1, startLap = None, endLap = None):
	"""
	If percent = 1, then n laps are taken. 
	Otherwise, the top % laps are taken i.e. if there are 50 laps and percent=0.5, the fastest 25 laps are returned.
	Inputs are driverID, season and round_number, with the optional startLap and endLap to refine which laps are returned.
	"""

	timed_laps = APIRequests.get_laps(season, round_number, driverID)[startLap:endLap]
	sorted_laps = sorted(timed_laps)
	
	if n>0 and percent == 1:
		L = n
	else:
		L = int(len(sorted_laps)*percent)+1
	lap_average = round(np.average(sorted_laps[:L]), 5)

	return timed_laps, sorted_laps, lap_average


