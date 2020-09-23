import re
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
    with open('mccTracker/data/mccData.json') as jsonFile:
        levelData = json.load(jsonFile)

    if 'error' in playerData['playerstats']:
        return playerData['playerstats']['error']

    fullUserData = {}

    for levelAchievement in levelData['achievements']:
        currentName = levelAchievement['name']
        currentGame = levelAchievement['game']
        currentLevel = levelAchievement['level']
        if currentGame not in fullUserData:
            fullUserData[currentGame] = {}
        if currentLevel not in fullUserData[currentGame]:
            fullUserData[currentGame][currentLevel] = {}
            fullUserData[currentGame][currentLevel]['totalAchievements'] = 0
            fullUserData[currentGame][currentLevel]['userAchievements'] = 0
        fullUserData[currentGame][currentLevel]['totalAchievements'] = fullUserData[currentGame][currentLevel]['totalAchievements'] + 1
        fullUserData[currentGame][currentLevel][currentName] = {}
        for achievement in playerData['playerstats']['achievements']:
            if achievement['apiname'] == currentName:     
                fullUserData[currentGame][currentLevel][currentName]['achieved'] = achievement['achieved']
                if fullUserData[currentGame][currentLevel][currentName]['achieved'] == 1:
                    fullUserData[currentGame][currentLevel][currentName]['unlockTime'] = datetime.strftime(datetime.fromtimestamp(achievement['unlocktime']),"%b %d %Y @ %I:%M %p")
                    fullUserData[currentGame][currentLevel]['userAchievements'] = fullUserData[currentGame][currentLevel]['userAchievements'] + 1
                else:
                    fullUserData[currentGame][currentLevel][currentName]['unlockTime'] = ""
        for mccAchievement in mccData['game']['availableGameStats']['achievements']:
            if mccAchievement['name'] == currentName:
                fullUserData[currentGame][currentLevel][currentName]['displayName'] = mccAchievement['displayName']
                fullUserData[currentGame][currentLevel][currentName]['description'] = mccAchievement['description']
                if fullUserData[currentGame][currentLevel][currentName]['achieved'] == 1:
                    fullUserData[currentGame][currentLevel][currentName]['icon'] = mccAchievement['icon']
                else:
                    fullUserData[currentGame][currentLevel][currentName]['icon'] = mccAchievement['icongray']
        
        for statsAchievement in achievementData['achievementpercentages']['achievements']:
            if statsAchievement['name'] == currentName:
                fullUserData[currentGame][currentLevel][currentName]['percent'] = round(statsAchievement['percent'],1)
    return fullUserData


def getSteamID(userName):
    if "https://steamcommunity.com/" in userName:
        userName = userName.split('/')[4]

    if re.search(r"^\d{17}$",userName):
        return userName
    else:
        steamIDURL = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key=" + key + "&vanityurl=" + userName
    
    steamID = json.loads(requests.get(steamIDURL).content)
    if steamID['response']['success'] == 1:
        return steamID['response']['steamid']
    else:
        return 0

def getSteamName(steamID):

    profileURL = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=" + key + "&steamids=" + steamID

    profile = json.loads(requests.get(profileURL).content)

    return profile['response']['players'][0]['personaname'], profile['response']['players'][0]['avatarmedium']