import json
import xml.etree.ElementTree as ET
import requests as req
import requests_cache as cache
import numpy as np

from . import APIRequests
from . import constants


cache.install_cache()



class Driver:
	driverID = ""

	def __init__(self, name):
		self.driverID = name
		driverGET = req.get("https://ergast.com/api/f1/drivers/{}.json".format(name))
		driverJSON = json.loads(driverGET.content)

		if len(driverJSON["MRData"]["DriverTable"]["Drivers"]) == 0:
			raise UnknownDriver("No such driver \"{}\" exists.".format(name))

		self.results = []
		self.raceID_participated = {} 	#dictionary season:roundsList
		self.lapsRace = {} 				#Keys are [season][round]
		self.raceResults = {} 			#raceResults[season][round] gives result

	def get_race_results(self):
		"""
		Gets all races participated in by the driver.
		
		"""
		limit = 30
		offset = 0
		raceResults = req.get("https://ergast.com/api/f1/drivers/{0}/results.json?offset={1}".format(self.driverID, offset))
		raceResults = json.loads(raceResults.content)
		totalResults = int(raceResults["MRData"]["total"])

		while offset + limit < totalResults:
			for race in raceResults["MRData"]["RaceTable"]["Races"]:
				if self.raceID_participated.get(int(race["season"]))== None:
					self.raceID_participated[int(race["season"])] = []
					self.raceResults[int(race["season"])] = {}

				self.raceID_participated[int(race["season"])].append(int(race["round"]))
				result = int(race["Results"][0]["position"])
				status = race["Results"][0]["status"]

				if status not in finishStatus:	
					result = -1
				self.raceResults[int(race["season"])][int(race["round"])] = result

			offset += limit
			raceResults = req.get("https://ergast.com/api/f1/drivers/{0}/results.json?offset={1}".format(self.driverID, offset))
			raceResults = json.loads(raceResults.content)

		return self.raceID_participated



	def get_lap_times(self, racesToCheck):
		"""
		Input of races to check, in the format as a list of tuples (season, round)
		Returns a dictionary with keys as [season][round] with only the races wanted(since the driver might have laps for other races)
		"""
		#Races to check should be a list of tuples (season, round)
		#If you want to add position functionality, position is lap["Timings"][0]["position"]
		#Lap number is index + 1(laps start at 1, indices at 0)
		self.laps = {}
		for race in racesToCheck:
			lapTimes = APIRequests.get_laps(race[0], race[1], self.driverID)

			if len(lapTimes["MRData"]["RaceTable"]["Races"][0]["Laps"]) == 0:
				self.laps[race[0]][race[1]] = []
				continue

			for lap in lapTimes["MRData"]["RaceTable"]["Races"][0]["Laps"]:
				self.lapsRace[race[0]][race[1]].append(get_sec(lap["Timings"][0]["time"]))

			self.laps[race[0]][race[1]] = self.lapsRace[race[0]][race[1]]

		return self.laps

	def save_pickle(self):
		with open("f1drivers_results/" + self.driverID + ".data", "wb") as driver_file:
			pickle.dump(self, driver_file)
			driver_file.close()

	@classmethod
	def load_driver(cls, driverID):
		"""
		Load driver by checking if a .data file exists with their class information.
		DriverID is a string in the form of "max_verstappen", "michael_schumacher", "vettel", etc... as used by Ergast API
		"""
		try:
			with open("f1drivers_results/" + driverID + ".data", "rb") as driver_file:
				driver = pickle.load(driver_file)
				driver_file.close()
		except:
			driver = None
			print("No driver found while loading!")
		return driver

	@classmethod
	def createDriverInstances(cls, driverIDList):
		"""
		Takes as input a list of driverID's and spits out a list of Driver classes associated to those drivers.
		If a class already exists then it is loaded, and if not it is created. 
		If the ID does not exist, an error is raised and it skips to the next driverID in the input list.
		"""
		driverList = []
		for driver in driverIDList:
			newDriver = Driver.load_driver(driver) #Attempts to load an existing driver before creating a new one
			if newDriver == None:
				try:
					newDriver = Driver(driver)
				except UnknownDriver as e:
					print(e.message)

			if newDriver != None:
				driverList.append(newDriver)

		return driverList


class UnknownDriver(BaseException):
	def __init__(self, message):
		self.message = message
	def __str__(self):
		return self.message

#dataset.plot(kind='box', subplots=True, layout=(2,2), sharex=False, sharey=False)

def get_sec(times):
	try:
		m,s = times.split(":")
	except ValueError:
		return 0
	return round(int(m)*60 + float(s), 4)

def get_lap_statistics(driverID, season, round_number, n, percent, startLap = None, endLap = None):
	pass
def head_to_head(driverTuple, season, round_number, n, percent, startLap = None, endLap = None):
	d1 = driverTuple[0]
	d2 = driverTuple[2]

	d1_timed_laps = d1.lapsRace[season][round_number]
	d2_timed_laps = d2.lapsRace[season][round_number]

	d1_sorted = sorted(d1_timed_laps)
	d2_sorted = sorted(d2_timed_laps)


def teammate_comparaisons(team, season, n, round_number, percent, startLap = None, endLap = None):
	"""
	team = [driverID1, driverID2, teamname]
	The driver ID's must be valid but the teamname is simply for record keeping and can even be 

	"""
	"""
	Returns formatted string for first 2 entries, and all lap times sorted
	Start/End lap compares between 2 laps (so from X to Y). By default 

	"""
	print("season {} round_number {} team[0] {}".format(season, round_number, team[0]))
	d1 = APIRequests.get_laps(season, round_number, team[0])
	d2 = APIRequests.get_laps(season, round_number, team[1])
#	d1=json.loads(req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/laps.json".format(season, round_number, team[0]) + lap_limit).content)
#	d2=json.loads(req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/laps.json".format(season, round_number, team[1]) + lap_limit).content)

	if len(d1["MRData"]["RaceTable"]["Races"]) != 0:
		d1_timed_laps =[get_sec(lap["Timings"][0]["time"]) for lap in d1["MRData"]["RaceTable"]["Races"][0]["Laps"]]
	else:
		d1_timed_laps = []

	if len(d2["MRData"]["RaceTable"]["Races"]) != 0:
		d2_timed_laps =[get_sec(lap["Timings"][0]["time"]) for lap in d2["MRData"]["RaceTable"]["Races"][0]["Laps"]]
	else:
		d2_timed_laps = []

	d1_timed_laps = d1_timed_laps[startLap:endLap]
	d2_timed_laps = d2_timed_laps[startLap:endLap]

	d1_sorted = sorted(d1_timed_laps)
	d2_sorted = sorted(d2_timed_laps)
	
	L1 = int(len(d1_sorted) * percent)+1 #Change to n if you want absolute number of laps
	L2 = int(len(d2_sorted) * percent)+1
	if n>0 and percent == 1:
		L1=n
		L2=n

	d1_avg = round(np.average(d1_sorted[:L1]),5)
	d2_avg = round(np.average(d2_sorted[:L2]),5)
	driver1_str = "{:<20}, {:<20}, {:<3}".format(team[0], d1_avg, len(d1_sorted))
	driver2_str = "{:<20}, {:<20}, {:<3}".format(team[1], d2_avg, len(d2_sorted))

	teammate_gap = d1_avg - d2_avg

	return driver1_str, driver2_str, d1_sorted, d2_sorted, teammate_gap, d1_timed_laps, d2_timed_laps
	
def qualifying_comparaison(team, season, round_number):
	#Takes team as a tuple of 2 drivers and teamname last

	d1=json.loads(req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/qualifying.json".format(season, round_number, team[0])).content)
	d2=json.loads(req.get("https://ergast.com/api/f1/{2}/{0}/drivers/{1}/qualifying.json".format(round_number, team[1], season)).content)

	qualiKey = "Q1" # changes depending on what year, in recent years there is q1 q2 q3 so use q3, in older years there is just 1 value for q1

	#Take only q3, might figure something better out later
	if qualiKey in d1["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"][0].keys():
		d1q3 = get_sec(d1["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"][0][qualiKey])
	else:
		d1q3 = None
	if qualiKey in d2["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"][0].keys():
		d2q3 = get_sec(d2["MRData"]["RaceTable"]["Races"][0]["QualifyingResults"][0][qualiKey])
	else:
		d2q3 = None

	return d1q3, d2q3

def rolling_average2(lapTimes, n=2):
	ret = np.cumsum(lapTimes, dtype=float)
	ret[n:] = ret[n:]-ret[:-n]
	return ret[n-1:]/n
def rolling_average(lapTimes, n=3):
	return np.convolve(lapTimes, np.ones(n), 'valid')/n

def rolling_laptimes(driverID, season, round_number, laps = 3, startLap = None, endLap = None):

	driverRequest = APIRequests.get_laps(season, round_number, driverID)

	if len(driverRequest["MRData"]["RaceTable"]["Races"]) != 0:
		timedLaps = np.array([get_sec(lap["Timings"][0]["time"]) for lap in driverRequest["MRData"]["RaceTable"]["Races"][0]["Laps"]])
		#print(timedLaps)
	else:
		#timedLaps = None
		return None

	rollingMeanLaptime = rolling_average(timedLaps[startLap:endLap], n=laps)
	return rollingMeanLaptime

def rolling_laptimes_chart(driverIDList, season, round_number, startLap = None, endLap = None, laps=3):
	x = np.arange(1+startLap, (endLap)-laps+2)
	
	roll = rolling_laptimes(driverID, season, round_number, startLap = startLap, endLap = endLap, laps=laps)
	plt.scatter(x, roll, color=driverColors[driverID])
	plt.plot(x, roll, color=driverColors[driverID])






#driverID = [	("max_verstappen", "perez", "Redbull"), 
#				("leclerc", "sainz", "Scuderia Ferrari"), 
#				("russell", "hamilton", "M*rcedes"), 
#				("alonso", "ocon", "Alphine")]
#driverID = [
#			("vettel", "webber", "Redbull"),
#			("hamilton", "button", "McLel"),
#			("alonso", "massa", "Scuderia Ferrari")]
#season = 2010
#avgPercentDef = {"Redbull":[], "McLel":[], "Scuderia Ferrari":[] }
#
#
#fileName = "2010_RB_SF_MC_pace_top20laps.csv"
#n=5 #number of laps

def createQualifyingComparaison(season, driverID, rounds = None):

	fileName = "1995_BENETTON_WILLIAMS_QUALIFYING.csv"
	sfCount, rbCount, mcCount = 0,0,0

	driverQuali = {}
	for key in driverID:
		driverQuali[key] = []

	if rounds == None:
		maxRound = json.loads(req.get("https://ergast.com/api/f1/{}.json".format(season)).content)["MRData"]["total"]
		maxRound = int(maxRound)
		rounds = [i for i in range(1, maxRound+1)]
	with open("f1data/Lap_Comparaisons/"+fileName, "w", newline = "", encoding="utf8") as csvfile:
		csvfile.write(",,")
		for team in driverID:
			format_string = "{},{},{},".format(team[0],team[1],team[2])
			csvfile.write(format_string)
		csvfile.write("\n")

		for round_number in rounds:
			raceName = json.loads(req.get("https://ergast.com/api/f1/{}/{}.json".format(season, round_number)).content)["MRData"]["RaceTable"]["Races"][0]["raceName"]
			csvfile.write("Qualifying results at the 2010 {0}, round{1},".format(raceName, round_number))
			print(round_number)
			avgQuali = []
	
			for team in driverID:
				#entry_string = "Quali for team {},".format(team[2])
				print(team, n, round_number)
				data_tuple = qualifying_comparaison(team, season, round_number)
				#driverQuali[team[0]].append(data_tuple[0])
				#driverQuali[team[1]].append(data_tuple[1])

				
	
				#Exclude if 10% slower since I'm assuming something happened
				if data_tuple[0] == None or data_tuple[1] == None:
					if data_tuple[0] == None: team_avg = data_tuple[1]
					if data_tuple[1] == None: team_avg = data_tuple[0]

				elif  data_tuple[0]>1.1*data_tuple[1]:
					team_avg = data_tuple[1]
				elif 1.1*data_tuple[0]<data_tuple[1]:
					team_avg = data_tuple[0]
				else:
					team_avg = np.average(data_tuple)

				format_string = "{},{},{},".format(data_tuple[0], data_tuple[1],team_avg)
				avgQuali.append(team_avg)

				csvfile.write(format_string)

			csvfile.write("\n")		
		csvfile.write(",Redbull, McLel, Ferrari\n")



def createLapComparaisonCSV(season,n,driverID, rounds = None, percent = 1):
	"""
	Creates for season
	if a tuple given for rounds, only checks those rounds(round = order in year so 1st race is 1, last race is usually 19 or 20 depending on season)
	Some stuff still need to be changed(sfcount and such at the end and deficit, need to make iterable version)
	n is number of laps to take into consideration(might change to percentage later, but it takes absolute number so top 20 laps)
	DriverID: List of tuples where first 2 are drivers, last one is the team
	If percent = 1 then n laps are taken, otherwise percent is used. 
	"""
	precision = 5 #Number of decimals to round
	teams = [team[2] for team in driverID]
	#teams = ["Ferrari", "McLel", "Bee Em Dubya"]
	print("teams are", teams)
	teams_str = "_".join(teams)
	#fileName = "2003_Bee_Em_Dubya_McLel_Ferrari_top30laps.csv" ##Filename to save as
	fileName = "{0}_{1}_top{2}laps_{3}.csv".format(season,teams_str,int(percent*100),rounds)

	performanceLimit = 1.1 #If a teammate performs this times worse it won't be considered in average 

	#percent = 1 #top % laps in decimal to take into consideration
	#Change percent to 1 so that n laps are taken

	#ToDo: create later, iterate over driverID where last field is teams to create these 2 stats
	#sfCount, rbCount, mcCount = 0,0,0
	#avgPercentDef = {"Redbull":[], "McLel":[], "Scuderia Ferrari":[] }

	avgPercentDef = {}
	for team in teams:
		avgPercentDef[team] = []




	if rounds == None:
		maxRound = json.loads(req.get("https://ergast.com/api/f1/{}.json".format(season)).content)["MRData"]["total"]
		maxRound = int(maxRound)
		rounds = [i for i in range(1, maxRound+1)]
	with open("f1data/Lap_Comparaisons/"+fileName, "w", newline = "", encoding="utf8") as csvfile:
		for round_number in rounds:
			raceName = json.loads(req.get("https://ergast.com/api/f1/{}/{}.json".format(season, round_number)).content)["MRData"]["RaceTable"]["Races"][0]["raceName"]
			print("{0} fastest laps".format(n))
			csvfile.write("{0} fastest laps at the {1} {2} Round {3}\n".format(n, season, raceName, round_number))
			print(round_number)
			averageLaps = {}
			for team in teams:
				averageLaps[team] = []
	
			for team in driverID:
				entry_string = "Race pace for team {}\n".format(team[2])
				print(team, n, round_number)
				data_tuple = teammate_comparaisons(team, season, n, round_number, percent)
				"""
				Format string has format:
				Driver 1, avg lap time, number of laps
				Driver 1 lap times(sorted fast to slowest)
				Driver 2, avg lap time, number of laps
				Driver 2 laptimes(fastest to slowest)
				"""
				format_string = "{0}\n,{1}\n{2}\n,{3}\n".format(data_tuple[0], str(data_tuple[2])[1:-1], data_tuple[1], str(data_tuple[3])[1:-1])

				uptoNlaps = int(percent * len(data_tuple[2]))+1 #Can change back to n if you want absolute laps
				if n>0 and percent == 1:
					uptoNlaps = n

				#print("WE ARE HERE", data_tuple[2], data_tuple[3])
				if (np.average(data_tuple[2][:uptoNlaps])> performanceLimit*np.average(data_tuple[3][:uptoNlaps]) or len(data_tuple[2]) + 1 < len(data_tuple[3])) and len(data_tuple[3]) != 0: #If driver 1 is a lot faster than driver 2 use only driver 1 (or a lot less laps)
					team_avg = np.average(data_tuple[3][:uptoNlaps])
				elif (performanceLimit * np.average(data_tuple[2])<np.average(data_tuple[3][:uptoNlaps]) or len(data_tuple[2]) > len(data_tuple[3]) + 1) and len(data_tuple[2]) != 0: #Flip of first case
					team_avg = np.average(data_tuple[2][:uptoNlaps])
				else: #One driver isn't abnormally slower than the other so both are used
					team_avg = np.average(data_tuple[2][:uptoNlaps] + data_tuple[3][:uptoNlaps])
				averageLaps[team[2]].append(team_avg)
	
				csvfile.write(entry_string)
				csvfile.write(format_string)
				csvfile.write("Team average: ,{}\n".format(team_avg))
				csvfile.write("Team gap(driver 1 to 2, {}".format(data_tuple[4]))
				csvfile.write("\n\n\n")
			
			csv_data = {}
			
			avgLapTimes = [averageLaps[team][-1] for team in teams]
			fastest_time = min(avgLapTimes)
			for team in teams:
				delta = averageLaps[team][-1]-fastest_time
				if delta > 3:
					avgPercentDef[team].append(None)
					csv_data[team] = None
					continue

				avgPercentDef[team].append(round(delta/fastest_time * 100, precision))
				csv_data[team] = round(delta, precision)

			
			#percent_string = np.array2string(np.divide(csv_data, fastest_time)*100, separator = ",", precision = 5)[1:-1]
			#csv_string = np.array2string(np.array(csv_data), separator = ",", precision = 5)[1:-1]

			csvfile.write("Team, Team Average, Deficit(s), Deficit(%)\n")
			for team in teams:
				csvfile.write("{0}, {1}, {2}, {3}\n".format(team, round(averageLaps[team][-1], precision), csv_data[team], avgPercentDef[team][-1]))
				print("Deficit {0} {1}".format(team, avgPercentDef[team][-1], precision))


			#csvfile.write(",{}\n".format(",".join(teams)))
			#csvfile.write("Deficit to fastest(s): ,{}\n".format(csv_string))
			#csvfile.write("Deficit to fastest(%): ,{}\n".format(percent_string))
			csvfile.write("\n\n\n")
	
		avgDeficit = []
		for team in teams:
			try:
				while True:
					avgPercentDef[team].remove(None)
			except ValueError:
				pass

			print(team, avgPercentDef[team], np.average(avgPercentDef[team]))
			avgDeficit.append(np.average(avgPercentDef[team]))
			csvfile.write("{},{}\n".format(team, str(avgPercentDef[team])[1:-1]))

		avgDeficit_string = np.array2string(np.array(avgDeficit), separator = ",", precision = 5)[1:-1]
		csvfile.write(",{}\n".format(",".join(teams)))
		csvfile.write("Average deficit(%),{0}\n".format(avgDeficit_string))


		#prettyPrint(teams, )


def getPtsSystem(season, drivers, ptsSystem):
	driverPts = {}
	for driver in drivers: 
		driverPts[driver] = []
		pts = 0
		for race in driver.raceResults[season].keys():
			driverPts[driver].append(ptsSystem[driver.raceResults[season][race]])
			pts += ptsSystem[driver.raceResults[season][race]]
	print(driver.driverID, season, pts)
	return driverPts
