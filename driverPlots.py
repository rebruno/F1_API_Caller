import json
import requests as req
import requests_cache as cache
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors 
from .driver import *
from .constants import *
from .APIRequests import *



def head_to_head_laptime(driverIDs, season, round_number, startLap = 0, endLap = None, laps = 0):
	"""
	If laps is provided, uses a rolling lap average over that many laps
	"""
	#Create plot 
	fig = plt.figure()
	gs = gridspec.GridSpec(2, 1, height_ratios=[3,1])
	laptimes = plt.subplot(gs[0])
	delta = plt.subplot(gs[1])
	raceName = get_race_name(season, round_number)
	lapTimeData = []

	#If laps is greater than 0, use a rolling average. Otherwise just compare raw laptimes
	if laps > 0:
		deltaTimes = rolling_laptimes(driverIDs[0], season, round_number, startLap = startLap, endLap = endLap, laps = laps)
	else:
		deltaTimesGET = get_laps(season, round_number, driverIDs[0])
		deltaTimes = np.array([get_sec(lap["Timings"][0]["time"]) for lap in deltaTimesGET["MRData"]["RaceTable"]["Races"][0]["Laps"]])[startLap:endLap]
		print(type(deltaTimes))#[startLap:endLap]

	for driver in driverIDs:
		if laps > 0:
			driverLaps = rolling_laptimes(driver, season, round_number, startLap = startLap, endLap = endLap, laps = laps)
		else:
			driverLapsGET = APIRequests.get_laps(season, round_number, driver)
			driverLaps = np.array([get_sec(lap["Timings"][0]["time"]) for lap in driverLapsGET["MRData"]["RaceTable"]["Races"][0]["Laps"]])[startLap:endLap]
		print(driverLaps)
		x = np.arange(1+startLap, len(driverLaps)+startLap+1)
	
		if driver not in driverColors.keys(): #Give a random color
			color = colors.hsv_to_rgb((np.random.randint(0, 256)/256, 1, 1))
		else:
			color = driverColors[driver]

		lapTimeData.append(driverLaps)
		
		laptimes.plot(x, driverLaps, color=color, label = driver)
		laptimes.scatter(x, driverLaps,color=color)

		minIndex = min([driverLaps.shape[0], deltaTimes.shape[0]])
		delta.scatter(x[:minIndex], driverLaps[:minIndex]-deltaTimes[:minIndex])

	xbound = laptimes.get_xbound()
	ybound = laptimes.get_ybound()

	xticks = np.arange(int(xbound[0]), int(xbound[1]))
	yticks = np.arange(int(ybound[0])-1, int(ybound[1])+1, 0.2)

	print(xbound, ybound)
	laptimes.set_xlabel("Lap number")
	laptimes.set_ylabel("Lap times [s]")
	laptimes.legend()
	#laptimes.set_xticks(xticks)
	#laptimes.set_yticks(yticks)
	laptimes.set_title("{}".format(raceName))
	laptimes.grid(linestyle="--", linewidth=0.5)

	xbound = delta.get_xbound()
	ybound = delta.get_ybound()

	delta.set_xlabel("Lap number")
	delta.set_ylabel("Lap times [s]")
	delta.axhline(y=0, lw = 0.5,  color = "k")
	delta.grid(linestyle="--", linewidth=0.5)

	fig.tight_layout()
	return fig, laptimes, delta, lapTimeData









