import json
import time
import requests
import configparser

from datetime import datetime

parser = configparser.ConfigParser()
parser.read('config.ini')
key = parser.get('keys','steamAPI')

def getUserData(steamAccountID):
    

    playerDataURL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=976730&key=" + key + "&steamid=" + steamAccountID
    mccDataURL = "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=976730&key=" + key
    achievementDataURL = "http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid=976730"

    playerData = json.loads(requests.get(playerDataURL).content)
    mccData = json.loads(requests.get(mccDataURL).content)
    achievementData = json.loads(requests.get(achievementDataURL).content)
    with open('data/mccData.json') as jsonFile:
        levelData = json.load(jsonFile)


    fullUserData = {}

    for achievement in playerData['playerstats']['achievements']:
        currentName = achievement['apiname']
        fullUserData[currentName] = {}
        fullUserData[currentName]['achieved'] = achievement['achieved']
        if fullUserData[currentName]['achieved'] == 1:
            fullUserData[currentName]['unlockTime'] = datetime.strftime(datetime.fromtimestamp(achievement['unlocktime']),"%b %d %Y @ %I:%M %p")
        else:
            fullUserData[currentName]['unlockTime'] = ""
        for mccAchievement in mccData['game']['availableGameStats']['achievements']:
            if mccAchievement['name'] == currentName:
                fullUserData[currentName]['displayName'] = mccAchievement['displayName']
                fullUserData[currentName]['description'] = mccAchievement['description']
                if fullUserData[currentName]['achieved'] == 1:
                    fullUserData[currentName]['icon'] = mccAchievement['icon']
                else:
                    fullUserData[currentName]['icon'] = mccAchievement['icongray']
        
        for statsAchievement in achievementData['achievementpercentages']['achievements']:
            if statsAchievement['name'] == currentName:
                fullUserData[currentName]['percent'] = round(statsAchievement['percent'],1)
        

        for levelAchievement in levelData['achievements']:
            if levelAchievement['name'] == currentName:
                fullUserData[currentName]['game'] = levelAchievement['game']
                fullUserData[currentName]['level'] = levelAchievement['level']
         
    return fullUserData

def getSteamID(userName):
    steamIDURL = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + key + "&vanityurl=" + userName
    steamID = json.loads(requests.get(steamIDURL).content)
    if steamID['response']['success'] == 1:
        return steamID['response']['steamid']
    else:
        return 0