import json
import requests as req
import requests_cache as cache
import numpy as np

from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors 

from .constants import *
from .APIRequests import *



def head_to_head_laptime(driverIDList, season, round_number, startLap = 0, endLap = None, laps = 0, cutoff=None):
	"""
	If laps is provided, uses a rolling lap average over that many laps. Otherwise it displays raw laptime.
	To use this, just pass a list of driver IDs, a season & round_number.
	You can also optionally pass a lap interval using startLap, endLap to focus on a certain stint.
	"""
	
	#Create plot 
	fig = plt.figure()
	gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
	laptimes = plt.subplot(gs[0])
	delta = plt.subplot(gs[1])
	raceName = get_race_name(season, round_number)
	lapTimeData = []

	#If laps is greater than 0, use a rolling average. Otherwise just compare raw laptimes
	#deltaTimes is essentially the laptimes of the first driver in the provided ID list subtracted from the driver being compared
	#Ideally the fastest driver/race winner would be passed first so that the results do not look weird
	if laps > 0:
		deltaTimes = rolling_laptimes(driverIDList[0], season, round_number, startLap = startLap, endLap = endLap, laps = laps)
	else:
		deltaTimes = get_laps(season, round_number, driverIDList[0])[startLap:endLap]

	for driver in driverIDList:
		if laps > 0:
			driverLaps = rolling_laptimes(driver, season, round_number, startLap = startLap, endLap = endLap, laps = laps)
		else:
			driverLaps= APIRequests.get_laps(season, round_number, driver)[startLap:endLap]
		if driverLaps is None:
			print("Driver {} has no laps. Check driverID".format(driver))
			continue
			
		x = np.arange(1+startLap, len(driverLaps)+startLap+1)

		color = get_color(driver)


		lapTimeData.append(driverLaps)
		
		laptimes.plot(x, driverLaps, color=color, label = driver)
		laptimes.scatter(x, driverLaps,color=color)

		#minIndex is there so that if 1 driver completed less laps than another, numpy correctly subtracts the deltaTimes.
		#Issues can arise if the first driver in the array hasn't completed the entire race
		minIndex = min([driverLaps.shape[0], deltaTimes.shape[0]])
		delta.scatter(x[:minIndex], driverLaps[:minIndex]-deltaTimes[:minIndex], color=color)

	laptimes.set_xlabel("Lap number")
	laptimes.set_ylabel("Lap times [s]")
	laptimes.legend()

	laptimes.set_title("{}".format(raceName))
	laptimes.grid(linestyle="--", linewidth=0.5)

	delta.set_xlabel("Lap number")
	delta.set_ylabel("Lap times [s]")
	delta.axhline(y=0, lw = 0.5,  color = "k")
	delta.grid(linestyle="--", linewidth=0.5)
	#delta.legend()

	fig.tight_layout()
	return fig, laptimes, delta, lapTimeData


def driver_lap_boxplot(driverIDList, season, round_number, startLap=None, endLap=None, exclude=-1, scatter=True):
	"""
	Creates a boxplot of laptimes for drivers provided at a race.
	If exclude is given a positive value, excludes any values that are greater than that threshold(given as a percentage)
	"""
	fig, ax = plt.subplots(1,1)
	raceName = get_race_name(season, round_number)
	lapTimeData = []
	position = 1

	for driver in driverIDList:

		driverLaps = APIRequests.get_laps(season, round_number, driver)[startLap:endLap]
		if driverLaps is None:
			print("Driver {} has no laps. Check driverID or if the driver started the Grand Prix.".format(driver))
			continue	

		if exclude>0:
			driverLaps = driverLaps[driverLaps<np.average(driverLaps)*exclude]

		lapTimeData.append(driverLaps)
		
		if scatter:
			color = get_color(driver)
			x = np.random.normal(position, 0.04, size=len(driverLaps))
			ax.scatter(x, driverLaps, color=color, alpha=0.3, label=driver)

		position+=1
	
	ax.boxplot(x=lapTimeData, labels=driverIDList)#, color=color)

	ax.set_xlabel("Drivers")
	ax.set_ylabel("Lap times[s]")
	ax.legend(loc="upper right")
	ax.grid(linestyle="--", linewidth=0.5)
	ax.set_title("{}".format(raceName))

	return fig, ax, lapTimeData


	







