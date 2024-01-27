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

    #This will vary depending on time-control, but i'm going to average 
    #over all controls of rapid, blitz, and so on. I don't think there's a reason to believe this
    #distribution should change with time, but we'll see. 
    def getMoveTimesDistribution(self, year, month, gameType):
        games = self.getRawGames(year, month)
        times = []
        for game in games:
            if(game['time_class'] == gameType):
                #First we will get the color of the player
                color = ""
                if(game['black']['username'] == self.userName):
                    color = "black"
                else:
                    color = "white"

                clockTimes = self.pgnExtractTimes(game['pgn'])

                for i in range(2,len(clockTimes)):
                    if(color == "white" and i%2 == 0):
                        times.append(clockTimes[i-2] - clockTimes[i])
                    elif(color == "black" and i%2 == 1):
                        times.append(clockTimes[i-2] - clockTimes[i])
                        

        maxData = np.max(times)
        minData = np.min(times)
        nBins = int(np.sqrt(len(times)))
        distribution = np.zeros(nBins)
        xValues = np.linspace(minData, maxData, nBins)
        

        for i in range(0,len(times)):
            point = times[i]
            bin = int(nBins*(point - minData)/(maxData - minData))
            if(bin == nBins):
                bin = bin - 1
            distribution[bin] = distribution[bin] + 1

        distribution = distribution/sum(distribution)

        return xValues, distribution


    def getMoveTimeDistributionInDay(self, year, month, day, gameType):
        games = self.getRawGames(year, month)
        times = []
        for game in games:
            gameDay = self.pgnExtractDay(game['pgn'])
            if(game['time_class'] == gameType and day == gameDay):
                #First we will get the color of the player
                color = ""
                if(game['black']['username'] == self.userName):
                    color = "black"
                else:
                    color = "white"
                clockTimes = self.pgnExtractTimes(game['pgn'])

                for i in range(2,len(clockTimes)):
                    if(color == "white" and i%2 == 0):
                        times.append(clockTimes[i-2] - clockTimes[i])
                    elif(color == "black" and i%2 == 1):
                        times.append(clockTimes[i-2] - clockTimes[i])
                        

        maxData = np.max(times)
        minData = np.min(times)
        nBins = int(np.sqrt(len(times)))
        distribution = np.zeros(nBins)
        xValues = np.linspace(minData, maxData, nBins)
        

        for i in range(0,len(times)):
            point = times[i]
            bin = int(nBins*(point - minData)/(maxData - minData))
            if(bin == nBins):
                bin = bin - 1
            distribution[bin] = distribution[bin] + 1

        distribution = distribution/sum(distribution)

        return xValues, distribution
        
                        
    def pgnExtractTimes(self, text):
        gameText = ""
        for line in text.splitlines():
            if(len(line) > 0 and line[0] != "[" and line[-1] != "]"):
                gameText = line
                break

        timeCutsUnclean = gameText.split("clk ")
        timeCutsUnclean = timeCutsUnclean[1:]
        timeCutsClean = []
        for i in range(0,len(timeCutsUnclean)):
            s = ""
            textChunk = timeCutsUnclean[i]
            index = 0
            while(textChunk[index] != "]"):
                s = s + textChunk[index]
                index = index + 1
            timeCutsClean.append(s)

        timeSeconds = []
        for i in range(0,len(timeCutsClean)):
            timeCutClean = timeCutsClean[i]
            timeSegments = timeCutClean.split(':')
            seconds = float(timeSegments[0])*60*60 + float(timeSegments[1])*60 + float(timeSegments[2])
            timeSeconds.append(seconds)
        return timeSeconds

    def pgnExtractDay(self, text):
        day = ""
        for line in text.splitlines():
            if("Date" in line):
                dateSplit = line.split(".")
                day = dateSplit[2][0:2]
                break

        return day
            
                    
                
        
        
                      
            

    