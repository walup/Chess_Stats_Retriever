import requests
import json
import io
import pandas as pd
import math
import numpy as np

class DataRetriever:
    
    def __init__(self, userName):
        self.userName = userName
        self.headers = ""

    def setUserAgent(self, userAgent):
        self.userAgent = userAgent

    def getRawGames(self, year, month):
        url = f"https://api.chess.com/pub/player/{self.userName}/games/{year}/{month}"
        if(self.userAgent != ""):
            data = requests.get(url,headers = {'User-Agent': self.userAgent})
        else:
            data = requests.get(url)
        if data.status_code != 200:
            raise Exception("The following response was returned: " + str(data.status_code))
        else:
            data = json.loads(data.text)
            games = data["games"]

        return games
        

    def getMonthEloProgression(self, year, month, gameType):
        url = f"https://api.chess.com/pub/player/{self.userName}/games/{year}/{month}"
        if(self.userAgent != ""):
            data = requests.get(url,headers = {'User-Agent': self.userAgent})
        else:
            data = requests.get(url)
        if data.status_code != 200:
            raise Exception("The following response was returned: " + str(data.status_code))
        else:
            data = json.loads(data.text)
            games = data["games"]

        eloArray = []

        for game in games:

            if(game['time_class'] == gameType):
                if(game['black']['username'] == self.userName):
                    eloArray.append(float(game['black']['rating']))
                else:
                    eloArray.append(float(game['white']['rating']))

        return eloArray

    def getEloMonthDistribution(self, year, month, gameType):
        eloData = self.getMonthEloProgression(year, month, gameType)
        maxData = np.max(eloData)
        minData = np.min(eloData)
        nBins = int(np.sqrt(len(eloData)))
        distribution = np.zeros(nBins)
        xValues = np.linspace(minData, maxData, nBins)
        

        for i in range(0,len(eloData)):
            point = eloData[i]
            bin = int(nBins*(point - minData)/(maxData - minData))
            if(bin == nBins):
                bin = bin - 1
            distribution[bin] = distribution[bin] + 1

        distribution = distribution/sum(distribution)

        return xValues, distribution
                      
            

    