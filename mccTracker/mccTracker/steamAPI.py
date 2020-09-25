import re
import json
import time
import requests
import configparser

from datetime import datetime

# Getting secrets 
parser = configparser.ConfigParser()
parser.read('config.ini')
key = parser.get('keys','steamAPI')


def getUserData(steamAccountID):

    # Setting up API URLs
    playerDataURL = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/?appid=976730&key=" + key + "&steamid=" + steamAccountID
    mccDataURL = "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?appid=976730&key=" + key
    achievementDataURL = "http://api.steampowered.com/ISteamUserStats/GetGlobalAchievementPercentagesForApp/v0002/?gameid=976730"

    # Getting and converting data from JSON to Python dictionaries 
    playerData = json.loads(requests.get(playerDataURL).content)
    mccData = json.loads(requests.get(mccDataURL).content)
    achievementData = json.loads(requests.get(achievementDataURL).content)
    with open('mccTracker/data/mccData.json') as jsonFile:
        levelData = json.load(jsonFile)

    # 'error' is a key give by Steam if no data is returned (doesnt own game or profile no public)
    if 'error' in playerData['playerstats']:
        return playerData['playerstats']['error']

    # Setting up dict to be returned
    fullUserData = {}
    
    # Start loop with our custom JSON to control ordering
    for levelAchievement in levelData['achievements']:
        currentName = levelAchievement['name']
        currentGame = levelAchievement['game']
        currentLevel = levelAchievement['level']
        if currentGame not in fullUserData: # Checking if the current game has been added to our dict
            fullUserData[currentGame] = {}
        if currentLevel not in fullUserData[currentGame]: # Checking if the current level has been added to our dict
            fullUserData[currentGame][currentLevel] = {}
            fullUserData[currentGame][currentLevel]['totalAchievements'] = 0 # Setting up achievement counter
            fullUserData[currentGame][currentLevel]['userAchievements'] = 0
        fullUserData[currentGame][currentLevel]['totalAchievements'] = fullUserData[currentGame][currentLevel]['totalAchievements'] + 1
        fullUserData[currentGame][currentLevel][currentName] = {} # Setting up achievement
        
        # Looping through players achievements then adding data to dict
        for achievement in playerData['playerstats']['achievements']:
            if achievement['apiname'] == currentName:     
                fullUserData[currentGame][currentLevel][currentName]['achieved'] = achievement['achieved']
                if fullUserData[currentGame][currentLevel][currentName]['achieved'] == 1:
                    fullUserData[currentGame][currentLevel][currentName]['unlockTime'] = datetime.strftime(datetime.fromtimestamp(achievement['unlocktime']),"%b %d %Y @ %I:%M %p")
                    fullUserData[currentGame][currentLevel]['userAchievements'] = fullUserData[currentGame][currentLevel]['userAchievements'] + 1
                else:
                    fullUserData[currentGame][currentLevel][currentName]['unlockTime'] = ""
        
        # Looping through game achievements then adding data to dict          
        for mccAchievement in mccData['game']['availableGameStats']['achievements']:
            if mccAchievement['name'] == currentName:
                fullUserData[currentGame][currentLevel][currentName]['displayName'] = mccAchievement['displayName']
                fullUserData[currentGame][currentLevel][currentName]['description'] = mccAchievement['description']
                if fullUserData[currentGame][currentLevel][currentName]['achieved'] == 1:
                    fullUserData[currentGame][currentLevel][currentName]['icon'] = mccAchievement['icon']
                else:
                    fullUserData[currentGame][currentLevel][currentName]['icon'] = mccAchievement['icongray']
        
        # Looping through staticts achievements then adding data to dict
        for statsAchievement in achievementData['achievementpercentages']['achievements']:
            if statsAchievement['name'] == currentName:
                fullUserData[currentGame][currentLevel][currentName]['percent'] = round(statsAchievement['percent'],1)
    return fullUserData


def getSteamID(userName):

    # Check for community URL
    if "https://steamcommunity.com/" in userName:
        userName = userName.split('/')[4]
    
    # SteamID is 17 numbers
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

    # Grab and return display name and avatar
    return profile['response']['players'][0]['personaname'], profile['response']['players'][0]['avatarmedium']