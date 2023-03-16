import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import requests

key = '1G6v0bQs4mo1fSbS6u8gaalKODDET6hSder9HRNeXsca986C9H2F1Vc2oafNVGfl'
baseURL = 'https://www.thebluealliance.com/api/v3/'
header = {'X-TBA-Auth-Key':key}
#This prevents us from repeatedly opening and closing a socket + speeds it up.
s = requests.Session()

def getTBA(url):
    #allows us to quickly call TBA api endpoints.
    return s.get(baseURL + url, headers=header).json()

def get_events(year):
    events = getTBA(f"events/{year}")
    namesAndKeys = []
    for event in events:
        toAppend = (event['name'], event['key'])
        namesAndKeys.append(toAppend)
    return namesAndKeys

def get_events_teams(event):
    teams = getTBA(f"event/{event}/teams")
    team_names = []
    for team in teams:
        team_names.append(f"{team['name']}, {team['key'][3:]}")
    return team_names

def competition_match_data(team, event):
    #This function returns a list of tuples for a team
    #tup format (event, match#, color, position)
    lst = []
    competition_level = None
    matches = getTBA("team/frc" + str(team) + "/event/" + event + "/matches")
    #print(matches[0])
    team_key = "frc" + str(team)
    for match in matches:
        matchNum = match["match_number"]
        if team_key in match["alliances"]["blue"]["team_keys"]:
            color = 'blue'
            position = match["alliances"]["blue"]["team_keys"].index(team_key)
        if team_key in match["alliances"]["red"]["team_keys"]:
            color = 'red'
            position = match["alliances"]["red"]["team_keys"].index(team_key)
        # Find if the match is a qualification, quarterfinal, semifinal, or final
        if match["comp_level"] == "qm":
            competition_level = "qm"
        elif match["comp_level"] == "qf":
            competition_level = "qf"
        elif match["comp_level"] == "sf":
            competition_level = "sf"
        elif match["comp_level"] == "f":
            competition_level = "f"
        # For a qf, sf, or f match, add the number and m after the competition_level from the match key (i.e. f1m, and sf1m)
        if competition_level != "qm":
            competition_level = competition_level + match["key"][-3] + "m"
        lst.append( (event, matchNum, color, position, competition_level, match["key"]) )
    return lst

# zebra data bla bla bla -ryan
def zebra_data_quarterfinals_pull(event, match, color, position, competition_level):
    data = getTBA("match/" + event + "_" + competition_level + str(match) + "/zebra_motionworks")
    times = data['times'] #List of times in 1 second interval for match
    xData = data["alliances"][color][position]['xs']
    if xData[0] == None:
        xData[0] = xData[1]
    if xData[-1] == None:
        xData[-1] = xData[-2]
    yData = data["alliances"][color][position]['ys']
    if yData[0] == None:
        yData[0] = yData[1]
    if yData[-1] == None:
        yData[-1] = yData[-2]

    for i in range(len(xData)):
        j = i
        try:
            if xData[i] == None:
                try:
                    xData[i] = (xData[j-1] + xData[j+1]) / 2
                except:
                    pass
                if xData[i] == None:
                    placeholder = False
                    try:
                        while xData[i] == None and j < len(xData):
                            j += 1
                            xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
            if xData[i] == None:
                xData.remove(xData[i])
        except:
            pass

    for i in range(len(yData)):
        j = i
        try:
            if yData[i] == None:
                try:
                    yData[i] = (yData[j-1] + yData[j+1]) / 2
                except:
                    pass
                if yData[i] == None:
                    placeholder = False
                    try:
                        while yData[i] == None and j < len(yData):
                            i += 1
                            yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
            if yData[i] == None:
                yData.remove(yData[i])
        except:
            pass

    return times, xData, yData

def zebra_data_semifinals_pull(event, match, color, position, competition_level):
    data = getTBA("match/" + event + "_" + competition_level + str(match) + "/zebra_motionworks")
    times = data['times'] #List of times in 1 second interval for match
    xData = data["alliances"][color][position]['xs']
    if xData[0] == None:
        xData[0] = xData[1]
    if xData[-1] == None:
        xData[-1] = xData[-2]
    yData = data["alliances"][color][position]['ys']
    if yData[0] == None:
        yData[0] = yData[1]
    if yData[-1] == None:
        yData[-1] = yData[-2]

    for i in range(len(xData)):
        j = i
        try:
            if xData[i] == None:
                try:
                    xData[i] = (xData[j-1] + xData[j+1]) / 2
                except:
                    pass
                if xData[i] == None:
                    placeholder = False
                    try:
                        while xData[i] == None and j < len(xData):
                            j += 1
                            xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
            if xData[i] == None:
                xData.remove(xData[i])
        except:
            pass

    for i in range(len(yData)):
        j = i
        try:
            if yData[i] == None:
                try:
                    yData[i] = (yData[j-1] + yData[j+1]) / 2
                except:
                    pass
                if yData[i] == None:
                    placeholder = False
                    try:
                        while yData[i] == None and j < len(yData):
                            i += 1
                            yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
            if yData[i] == None:
                yData.remove(yData[i])
        except:
            pass

    return times, xData, yData

def zebra_data_finals_pull(event, match, color, position, competition_level):
    data = getTBA("match/" + event + "_" + competition_level + str(match) + "/zebra_motionworks")
    times = data['times'] #List of times in 1 second interval for match
    xData = data["alliances"][color][position]['xs']
    if xData[0] == None:
        xData[0] = xData[1]
    if xData[-1] == None:
        xData[-1] = xData[-2]
    yData = data["alliances"][color][position]['ys']
    if yData[0] == None:
        yData[0] = yData[1]
    if yData[-1] == None:
        yData[-1] = yData[-2]

    for i in range(len(xData)):
        j = i
        try:
            if xData[i] == None:
                try:
                    xData[i] = (xData[j-1] + xData[j+1]) / 2
                except:
                    pass
                if xData[i] == None:
                    placeholder = False
                    try:
                        while xData[i] == None and j < len(xData):
                            j += 1
                            xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
            if xData[i] == None:
                xData.remove(xData[i])
        except:
            pass

    for i in range(len(yData)):
        j = i
        try:
            if yData[i] == None:
                try:
                    yData[i] = (yData[j-1] + yData[j+1]) / 2
                except:
                    pass
                if yData[i] == None:
                    placeholder = False
                    try:
                        while yData[i] == None and j < len(yData):
                            i += 1
                            yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
            if yData[i] == None:
                yData.remove(yData[i])
        except:
            pass

    return times, xData, yData

def zebra_data_pull(event, match, color, position):
    data = getTBA("match/" + event + "_qm" + str(match) + "/zebra_motionworks")
    times = data['times'] #List of times in 1 second interval for match
    xData = data["alliances"][color][position]['xs']
    if xData[0] == None:
        xData[0] = xData[1]
    if xData[-1] == None:
        xData[-1] = xData[-2]
    yData = data["alliances"][color][position]['ys']
    if yData[0] == None:
        yData[0] = yData[1]
    if yData[-1] == None:
        yData[-1] = yData[-2]

    for i in range(len(xData)):
        j = i
        try:
            if xData[i] == None:
                try:
                    xData[i] = (xData[j-1] + xData[j+1]) / 2
                except:
                    pass
                if xData[i] == None:
                    placeholder = False
                    try:
                        while xData[i] == None and j < len(xData):
                            j += 1
                            xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        xData[i] = xData[j]
                        if xData[i] != None:
                            placeholder = True
            if xData[i] == None:
                xData.remove(xData[i])
        except:
            pass

    for i in range(len(yData)):
        j = i
        try:
            if yData[i] == None:
                try:
                    yData[i] = (yData[j-1] + yData[j+1]) / 2
                except:
                    pass
                if yData[i] == None:
                    placeholder = False
                    try:
                        while yData[i] == None and j < len(yData):
                            i += 1
                            yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
                    except:
                        pass
                    while placeholder == False and j > 0:
                        j-= 1
                        yData[i] = yData[j]
                        if yData[i] != None:
                            placeholder = True
            if yData[i] == None:
                yData.remove(yData[i])
        except:
            pass

    return times, xData, yData
def pythagorean_theorem(a, b):
    c = math.sqrt(math.pow(a,2) + math.pow(b,2))
    return c


def zebra_speed(times, xData, yData):
    speeds = []
    times = times
    xData = xData
    yData = yData
    i = 0
    j = 1
    while j < len(times):
        try:
            deltaX = xData[j] - xData[i]
            deltaY = yData[j] - yData[i]
            speeds.append(pythagorean_theorem(deltaX, deltaY) / .1)
        except:
            pass
        i += 1
        j += 1
    return speeds

def get_zoneData(team, event, match, times, xData, yData):
    zoneData = []
    i = 0
    try:
        while i < len(times):
            #in zone1?
            if xData[i] > 27 and yData[i] < 13.5:
                zoneData.append("Zone1")
            #in zone2?
            if xData[i] < 27 and yData[i] < 13.5:
                zoneData.append("Zone2")
            #in zone3?
            if xData[i] < 27 and yData[i] > 13.5:
                zoneData.append("Zone3")
            #in zone4?
            if xData[i] > 27 and yData[i] > 13.5 :
                zoneData.append("Zone4")
            if 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3:
                zoneData.append("RedCharging")
            i += 1
    except:
        pass
    return zoneData

def get_chargeStationDataEndgame(team, event, match, times, xData, yData):
    chargeStationData = []
    i = 0
    try:
        while i < len(times):
            if i > 150:
                if 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3:
                    chargeStationData.append("RedCharging")
                else:
                    chargeStationData.append("NotCharging")
                i += 1
            else:
                i += 1
    except:
        pass
    return chargeStationData

def get_chargeStationDataAuto(team, event, match, times, xData, yData):
    chargeStationData = []
    i = 0
    try:
        while i < len(times):
            if i < 150:
                if 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3:
                    chargeStationData.append("RedCharging")
                else:
                    chargeStationData.append("NotCharging")
                i += 1
            else:
                i += 1
    except:
        pass
    return chargeStationData

def get_timeChargingEndgame(team, event, match, times, xData, yData):
    chargeData = get_chargeStationDataEndgame(team, event, match, times, xData, yData)
    timeCharging = 0
    i = 0
    try:
        while i < len(chargeData):
            if chargeData[i] == "RedCharging":
                timeCharging += 1
            i += 1
    except:
        pass
    # / 10 to convert to seconds
    return timeCharging / 10

def get_timeChargingAuto(team, event, match, times, xData, yData):
    chargeData = get_chargeStationDataAuto(team, event, match, times, xData, yData)
    timeCharging = 0
    i = 0
    try:
        while i < len(chargeData):
            if chargeData[i] == "RedCharging":
                timeCharging += 1
            i += 1
    except:
        pass
    # / 10 to convert to seconds
    return timeCharging / 10

# Gather the data for Auto Charge Station from thebluealliance API --- use the score_breakdown dictionary
def get_autoChargeConfirmation(match_key, alliance, position):
        # Check if the team docked, parked, engaged, or did nothing in auto on the charge station
    try:
        # print the score_breakdown dictionary
        match_info = getTBA("match/" + match_key)
        score_breakdown = match_info["score_breakdown"]
        charging = score_breakdown[alliance][f"autoChargeStationRobot{position}"]
        return charging
        #return score_breakdown
    except:
        pass

def get_cycleData(match_key, alliance, times, xData):
    crossing_left = False
    crossing_right = False
    cross_back = False
    just_crossed_left = False
    just_crossed_right = False
    time_to_cross = []
    current_time_crossing = 0
    times_crossed = 0
    
    if alliance == "red":
        i = 0
        while i < len(times):
            if 38.25 > xData[i] > 16.5 and not crossing_left and not just_crossed_left:
                crossing_left = True
                time_to_cross.append(0)
            if crossing_left:
                time_to_cross[current_time_crossing] += 1
            if xData[i] > 38.25 and crossing_left:
                times_crossed += 1
                current_time_crossing += 1
                crossing_left = False
                just_crossed_left = True
            if 38.25 > xData[i] > 16.5 and not crossing_right and just_crossed_left:
                crossing_right = True
                time_to_cross.append(0)
            if crossing_right:
                time_to_cross[current_time_crossing] += 1
            if xData[i] < 16.5 and crossing_right:
                times_crossed += 1
                current_time_crossing += 1
                crossing_right = False
                just_crossed_left = False
            
            i += 1

        for j in range(0, len(time_to_cross)):
            time_to_cross[j] = time_to_cross[j] / 10

    if alliance == "blue":
        i = 0
        while i < len(times):
            if 38.25 > xData[i] > 16.5 and not crossing_right and not just_crossed_right:
                crossing_right = True
                time_to_cross.append(0)
            if crossing_right:
                time_to_cross[current_time_crossing] += 1
            if xData[i] < 16.5 and crossing_right:
                times_crossed += 1
                current_time_crossing += 1
                crossing_right = False
                just_crossed_right = True
            if 38.25 > xData[i] > 16.5 and not crossing_left and just_crossed_right:
                crossing_left = True
                time_to_cross.append(0)
            if crossing_left:
                time_to_cross[current_time_crossing] += 1
            if xData[i] > 38.25 and crossing_left:
                times_crossed += 1
                current_time_crossing += 1
                crossing_left = False
                just_crossed_right = False
            
            i += 1

        for j in range(0, len(time_to_cross)):
            time_to_cross[j] = time_to_cross[j] / 10

    try:
        avg_time_to_cross = sum(time_to_cross) / len(time_to_cross)
    except:
        avg_time_to_cross = 7777
    
    return avg_time_to_cross, times_crossed

def zebra_speed_percentile_graph(speeds, team, matchNumber, figure):
    plt.clf()
    try:
        percents = []
        i = 0
        while i < 95:
            percents.append(np.percentile(speeds,i))
            i += 1
        plt.figure(figure)
        plt.hist(percents, 100)
        plt.title("FRC " + str(team) + " Match #" + str(matchNumber))
        plt.xlabel("Speed (ft/s)")
        plt.ylabel("Percentile")
        #plt.show()
        #plt.savefig("564_data_Percentile/FRC" + str(team) + "Match" + str(matchNumber) + ".pdf")
        return plt
    except:
        return 7

def zebra_zone_percentile_piegraph(zoneData, team, matchNumber, allianceColor, matchType):
    plt.clf()
    try:
        zone1Count = zoneData.count("Zone1")
        zone2Count = zoneData.count("Zone2")
        zone3Count = zoneData.count("Zone3")
        zone4Count = zoneData.count("Zone4")
        if zone1Count == 0:
            labels = ['Zone2', 'Zone3', 'Zone4']
            sizes = [zone2Count, zone3Count, zone4Count]
        elif zone2Count == 0:
            labels = ['Zone1', 'Zone3', 'Zone4']
            sizes = [zone1Count, zone3Count, zone4Count]
        elif zone3Count == 0:
            labels = ['Zone1', 'Zone2', 'Zone4']
            sizes = [zone1Count, zone2Count, zone4Count]
        elif zone4Count == 0:
            labels = ['Zone1', 'Zone2', 'Zone3']
            sizes = [zone1Count, zone2Count, zone3Count]
        else:
            labels = ['Zone1', 'Zone2', 'Zone3', 'Zone4']
            sizes = [zone1Count, zone2Count, zone3Count, zone4Count]
        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
        ax1.axis('equal')
        plt.title("FRC " + str(team) + " " + matchType + " Match #" + str(matchNumber))
        # Make the background color the allianceColor
        fig1.set_facecolor(allianceColor)
        #plt.savefig("564_data_Percentile/FRC" + str(team) + "Match" + str(matchNumber) + ".pdf")
        return plt
    except:
        return 7