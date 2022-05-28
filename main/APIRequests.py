import json
import requests as req
import requests_cache as cache
import numpy as np
import re

from .constants import *
from .methods import *


def get_laps(season, round_number, driverID):
	"""
	Takes a season, round, and driverID and returns a list of their laptimes for that specific race.
	"""
	requestGET = req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/laps.json".format(season, round_number, driverID)+lap_limit)
	if requestGET.status_code > 400:
		return np.array([])

	lapTimesJSON = json.loads(requestGET.content)
	if len(lapTimesJSON["MRData"]["RaceTable"]["Races"]) == 0:
		return np.array([])
	lapTimes = np.array([get_sec(lap["Timings"][0]["time"]) for lap in lapTimesJSON["MRData"]["RaceTable"]["Races"][0]["Laps"]])

	return lapTimes

def get_races(seasonList):
	"""
	Takes as input a list of seasons(years) and gets all the races(# of rounds essentially)
	Returns a tuple (seaason, round)
	"""
	seasonRounds = []

	for season in seasonList:
		seasonReq = req.get("http://ergast.com/api/f1/{0}.json".format(season))
		seasonReq = json.loads(seasonReq.content)
		for i in range(int(seasonReq["MRData"]["total"])):
			seasonRounds.append(season, i)

	return seasonRounds

def get_drivers(season, round_number):
	"""
	Returns a list of all drivers that participated in a given Grand Prix.
	The values are the driverIDs used in API calls.
	"""
	driverIDList = []
	
	raceReq = req.get("https://ergast.com/api/f1/{0}/{1}/driverStandings.json".format(season,round_number))
	raceJson = json.loads(raceReq.content)
	for driverReq in raceJson["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
		driverIDList.append(driverReq["Driver"]["driverId"])
	return driverIDList


def get_race_name(season, round_number, year=False):
	"""
	Takes a season and round number, and returns the grand prix name.
	If year is passed as True, then it returns the year number + Grand Prix e.g.: 2022 Bahrain Grand Prix
	"""
	raceNameGET = req.get("https://ergast.com/api/f1/{}/{}.json".format(season, round_number))
	raceName = json.loads(raceNameGET.content)["MRData"]["RaceTable"]["Races"][0]["raceName"]
	if year != False:
		return "{} {}".format(season, raceName)
	return raceName


def get_quali(season, round_number, driverID):
	"""
	Gets qualifying results for that particular Grand Prix.
	If invalid, or no result for that GP(crashed in qualifying/practice, withdrew, etc..) an empty array is returned.
	Otherwise an array with the result for each qualifying(if there is more than one) is returned.
	Results returned in order of Q1, Q2, Q3.
	"""

	if type(season) != int or type(round_number) != int:
		print("Season and round number must be integers.")
		return np.array([])

	qualiRequest = req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/qualifying.json".format(season, round_number, driverID))
	if qualiRequest.status_code >= 400:
		return np.array([])

	qualiResult = json.loads(qualiRequest.content)

	qualiResult = qualiResult["MRData"]["RaceTable"]["Races"]
	if qualiResult == []:
		return np.array([])


	results = []
	for key in qualiKeys:
		if key in qualiResult[0]["QualifyingResults"][0].keys():
			results.append(get_sec(qualiResult[0]["QualifyingResults"][0][key]))

	return np.array(results)

def get_id(name):
	"""
	Takes as input some name, returns a driverID:full name dictionary.
	Search is case insensitive.
	Ex: If "schumacher" is passed as the name, then the dictionary
	{	'ralf_schumacher': 'Ralf Schumacher', 
		'michael_schumacher': 'Michael Schumacher', 
		'mick_schumacher': 'Mick Schumacher'}
	is returned.
	"""

	possibleDrivers = {}

	offset = 0
	limit = 100

	driverReq = req.get("https://ergast.com/api/f1/drivers.json?offset={0}&limit={1}".format(offset, limit))
	driverJSON = json.loads(driverReq.content)
	total = int(driverJSON["MRData"]["total"])

	#Check all first and last names, and driverIDs for a match. Case insensitive
	while offset + limit < total:
		for driver in driverJSON["MRData"]["DriverTable"]["Drivers"]:
			searchString = str([driver["driverId"], driver["givenName"], driver["familyName"]])[1:-1]
			
			searchResult = re.search(name, searchString, re.IGNORECASE)
			if searchResult != None:
				possibleDrivers[driver["driverId"]] = "{} {}".format(driver["givenName"], driver["familyName"])

		offset += limit
		driverReq = req.get("https://ergast.com/api/f1/drivers.json?offset={0}&limit={1}".format(offset, limit))
		driverJSON = json.loads(driverReq.content)

	return possibleDrivers



