import json
import xml.etree.ElementTree as ET
import requests as req
import requests_cache as cache
import numpy as np
from .constants import *



def get_laps(season, round_number, driverID):
	"""
	Takes a season, round, and driverID and returns a list of their laptimes for that specific race.
	"""
	requestGET = req.get("https://ergast.com/api/f1/{0}/{1}/drivers/{2}/laps.json".format(season, round_number, driverID)+lap_limit)
	lapTimes = json.loads(requestGET.content)
	return lapTimes

def get_races(seasonList):
	#Takes as input a list of seasons(years) and gets all the races(# of rounds essentially)
	#returns a tuple (seaason, round)
	seasonRounds = []

	for season in seasonList:
		seasonReq = req.get("http://ergast.com/api/f1/{0}.json".format(season))
		seasonReq = json.loads(seasonReq.content)
		for i in range(int(seasonReq["MRData"]["total"])):
			seasonRounds.append(season, i)

	return seasonRounds

def get_drivers(season, round_number):
	driverIDList = []
	
	raceReq = req.get("https://ergast.com/api/f1/{0}/{1}/driverStandings.json".format(season,round_number))
	raceJson = json.loads(raceReq.content)
	for driverReq in raceJson["MRData"]["StandingsTable"]["StandingsLists"][0]["DriverStandings"]:
		driverIDList.append(driverReq["Driver"]["driverId"])
	return driverIDList