import json
import requests as req
import requests_cache as cache
import numpy as np

from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib import colors 

from .constants import *
from .APIRequests import *



def head_to_head_laptime(driverIDs, season, round_number, startLap = 0, endLap = None, laps = 0, cutoff=None):
	"""
	If laps is provided, uses a rolling lap average over that many laps. Otherwise it displays raw laptime.
	To use this, just pass a list of driverIDs, a season & round_number.
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
		deltaTimes = rolling_laptimes(driverIDs[0], season, round_number, startLap = startLap, endLap = endLap, laps = laps)
	else:
		deltaTimes = get_laps(season, round_number, driverIDs[0])[startLap:endLap]

	for driver in driverIDs:
		if laps > 0:
			driverLaps = rolling_laptimes(driver, season, round_number, startLap = startLap, endLap = endLap, laps = laps)
		else:
			driverLaps= APIRequests.get_laps(season, round_number, driver)[startLap:endLap]
		if driverLaps is None:
			print("Driver {} has no laps. Check driverID".format(driver))
			continue
			
		x = np.arange(1+startLap, len(driverLaps)+startLap+1)


		#If the driver doesn't have a color assigned to them already, use a randomly generated one.
		if driver not in driverColors.keys(): 
			color = colors.hsv_to_rgb((np.random.randint(0, 256)/256, 1, 1))
		else:
			color = driverColors[driver]

		lapTimeData.append(driverLaps)
		
		laptimes.plot(x, driverLaps, color=color, label = driver)
		laptimes.scatter(x, driverLaps,color=color)

		#minIndex is there so that if 1 driver completed less laps than another, numpy correctly subtracts the deltaTimes.
		#Issues can arise if the first driver in the array hasn't completed the entire race
		minIndex = min([driverLaps.shape[0], deltaTimes.shape[0]])
		delta.scatter(x[:minIndex], driverLaps[:minIndex]-deltaTimes[:minIndex], color=color)

	xbound = laptimes.get_xbound()
	ybound = laptimes.get_ybound()

	xticks = np.arange(int(xbound[0]), int(xbound[1]))
	yticks = np.arange(int(ybound[0])-1, int(ybound[1])+1, 0.2)

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
	#delta.legend()

	fig.tight_layout()
	return fig, laptimes, delta, lapTimeData



def rolling_laptimes_chart(driverIDList, season, round_number, startLap = None, endLap = None, laps=3):
	x = np.arange(1+startLap, (endLap)-laps+2)
	
	roll = rolling_laptimes(driverID, season, round_number, startLap = startLap, endLap = endLap, laps=laps)
	plt.scatter(x, roll, color=driverColors[driverID])
	plt.plot(x, roll, color=driverColors[driverID])





