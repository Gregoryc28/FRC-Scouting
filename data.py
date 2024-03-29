import traceback

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

def get_matches(event):
    matches = getTBA(f"event/{event}/matches")
    return matches

def competition_match_data_all(event):
    # This function returns a list of tuples for all matches
    # tup format (match#, teams_in_match)
    lst = []
    matches = getTBA("event/" + event + "/matches")
    for match in matches:
        
        # Check what type of match it is
        if match["comp_level"] == "qm":
            competition_level = "Qualification-Match"
        elif match["comp_level"] == "qf":
            competition_level = "Quarter-Final"
        elif match["comp_level"] == "sf":
            competition_level = "Semi-Final"
        elif match["comp_level"] == "f":
            competition_level = "Final"

        # If the match is a qf, sf, or f, then we need to make sure we add which round it is
        if competition_level != "Qualification-Match":
            set_number = match["set_number"]
            competition_level += f" ({set_number})"

        matchNum = match["match_number"]

        matchNum = competition_level + " " + str(matchNum)

        teams = match["alliances"]["blue"]["team_keys"] + match["alliances"]["red"]["team_keys"]
        lst.append((matchNum, teams, competition_level, match["match_number"], match["key"]))
    return lst

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

def get_teleopChargeConfirmation(match_key, alliance, position):
        # Check if the team docked, parked, engaged, or did nothing in auto on the charge station
    try:
        # print the score_breakdown dictionary
        match_info = getTBA("match/" + match_key)
        score_breakdown = match_info["score_breakdown"]
        charging = score_breakdown[alliance][f"teleopChargeStationRobot{position}"]
        return charging
        #return score_breakdown
    except:
        pass

def calc_distance(xData1, xData2, yData1, yData2):
    try:
        distance = math.sqrt(math.pow(xData1 - xData2, 2) + math.pow(yData1 - yData2, 2))
        return distance
    except:
        return 7777


def get_cycleData(match_key, alliance, times, xData, yData):
    crossing_left = False
    crossing_right = False
    cross_back = False
    just_crossed_left = False
    just_crossed_right = False
    reached_loading_zone = False
    time_to_cross = []
    current_time_crossing = 0
    times_crossed = 0
    distance_travelled = []
    
    if alliance == "red":
        i = 0
        while i < len(times):
            # Check if the robot has crossed to the blue side and back.
            if 38.25 > xData[i] > 16.5 and not crossing_right and not just_crossed_right:
                crossing_right = True
                time_to_cross.append(0)
                distance_travelled.append(0)
            if crossing_right:
                # Add to the distance travelled the correct amount of distance
                try:
                    distance_travelled[current_time_crossing] += calc_distance(xData[i], xData[i-1], yData[i], yData[i-1])
                except:
                    pass
                time_to_cross[current_time_crossing] += 1
            if xData[i] < 16.5 and crossing_right and reached_loading_zone:
                times_crossed += 1
                current_time_crossing += 1
                crossing_right = False
                just_crossed_right = True
                reached_loading_zone = False
            if xData[i] > 38.25 and just_crossed_right:
                just_crossed_right = False
            if xData[i] < 16.5 and crossing_right:
                reached_loading_zone = True
            
            i += 1

        for j in range(0, len(time_to_cross)):
            time_to_cross[j] = time_to_cross[j] / 10

    if alliance == "blue":
        i = 0
        while i < len(times):
            # Check if the robot has crossed to the red side and back.
            if 38.25 > xData[i] > 16.5 and not crossing_left and not just_crossed_left:
                crossing_left = True
                time_to_cross.append(0)
                distance_travelled.append(0)
            if crossing_left:
                # Add to the distance travelled the correct amount of distance
                try:
                    distance_travelled[current_time_crossing] += calc_distance(xData[i], xData[i-1], yData[i], yData[i-1])
                except:
                    pass
                time_to_cross[current_time_crossing] += 1
            if xData[i] > 38.25 and crossing_left and reached_loading_zone:
                times_crossed += 1
                current_time_crossing += 1
                crossing_left = False
                just_crossed_left = True
                reached_loading_zone = False
            if xData[i] < 16.5 and just_crossed_left:
                just_crossed_left = False
            if xData[i] > 38.25 and crossing_left:
                reached_loading_zone = True
            
            i += 1

        for j in range(0, len(time_to_cross)):
            time_to_cross[j] = time_to_cross[j] / 10

    try:
        avg_time_to_cross = sum(time_to_cross) / len(time_to_cross)
    except:
        avg_time_to_cross = 7777
    
    try:
        average_distance_travelled = sum(distance_travelled) / len(distance_travelled)
    except:
        average_distance_travelled = 7777

    return avg_time_to_cross, times_crossed, average_distance_travelled

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

def get_team_match_videos(team, match_key):
    try:
        match_info = getTBA("match/" + match_key)
        match_videos = match_info['videos']
        # Get only one video from each match
        for video in match_videos:
            if video['type'] == 'youtube':
                return video['key']
    except:
        return 7

def average_speed(times, xData, yData):
    # Return the average speed using the zebra data
    # First get the zebra_speeds for the team and match, which means you need times, xData, and yData
    # Then use the zebra_speeds function to get the speeds
    try:
        speeds = zebra_speed(times, xData, yData)
        for speed in speeds:
            if speed > 20:
                speeds.remove(speed)
        avg_speed = sum(speeds) / len(speeds)
        return avg_speed
    except:
        return 7777

def average_speed_topPercentile(times, xData, yData):
    try:
        # First find the average speed
        avg_speed = average_speed(times, xData, yData)
        # Then, when creating the new average speed for this method, only include the speeds that are greater than the average speed
        speeds = zebra_speed(times, xData, yData)
        speeds = [x for x in speeds if x > avg_speed]
        avg_speed_topPercentile = sum(speeds) / len(speeds)
        return avg_speed_topPercentile
    except:
        return 7777

def max_speed(times, xData, yData):
    try:
        speeds = zebra_speed(times, xData, yData)
        # Remove any outlandish speeds from the speeds list
        for speed in speeds:
            if speed > 20:
                speeds.remove(speed)
        max_speed = max(speeds)
        return max_speed
    except:
        return 7777

def team_performance(team, event):
    # Create multiple lists for each performance metric.
    # Track metrics such as win, losses, and ties. Be sure to calculate win percentage aswell.
    # Also, track metrics such as average match score

    # Loop through each match and add the data to the lists
    wins = 0
    losses = 0
    ties = 0
    match_scores = []
    win_percentage = 0
    average_match_score = 0

    try:
        match_list = getTBA("team/frc" + team + "/event/" + event + "/matches")
        # Sort the matches in match_list by match number
        match_list = sorted(match_list, key=lambda k: k['match_number'])
        for match in match_list:
            if match['score_breakdown'] is not None:
                if match['alliances']['red']['team_keys'][0][3:] == team or match['alliances']['red']['team_keys'][1][3:] == team or match['alliances']['red']['team_keys'][2][3:] == team:
                    if match['alliances']['red']['score'] > match['alliances']['blue']['score']:
                        wins += 1
                    elif match['alliances']['red']['score'] < match['alliances']['blue']['score']:
                        losses += 1
                    else:
                        ties += 1
                else:
                    if match['alliances']['blue']['score'] > match['alliances']['red']['score']:
                        wins += 1
                    elif match['alliances']['blue']['score'] < match['alliances']['red']['score']:
                        losses += 1
                    else:
                        ties += 1
        win_percentage = round(wins / (wins + losses + ties) * 100, 2)
    except:
        pass

    # Also calculate the teams average speed
    average_speed = 0
    average_speed_top_percentile = 0
    match_speeds = []
    try:
        match_list = getTBA("team/frc" + team + "/event/" + event + "/matches")
        for match in match_list:
            # append the average speed of the match to the list
            if (average_speed(team, match['key']) != 7777):
                match_speeds.append(average_speed(team, match['key']))
            else:
                pass
            if (average_speed_topPercentile(team, match['key']) != 7777):
                match_speeds.append(average_speed_topPercentile(team, match['key']))
            else:
                pass
        average_speed = sum(match_speeds) / len(match_speeds)
    except:
        pass

    # Also calculate the average points in auto and teleop
    average_auto_points = 0
    average_teleop_points = 0
    auto_points = []
    teleop_points = []
    comp_levels = []
    try:
        match_list = getTBA("team/frc" + team + "/event/" + event + "/matches")
        # Sort the matches in match_list by match number
        match_list = sorted(match_list, key=lambda k: k['match_number'])
        for match in match_list:
            # Check if the match is finished
            if match['score_breakdown'] is not None:
                comp_levels.append(match['comp_level'])
                if match['alliances']['red']['team_keys'][0][3:] == team or match['alliances']['red']['team_keys'][1][3:] == team or match['alliances']['red']['team_keys'][2][3:] == team:
                    auto_points.append(match['score_breakdown']['red']['autoPoints'])
                    teleop_points.append(match['score_breakdown']['red']['teleopPoints'])
                    match_scores.append(match['score_breakdown']['red']['autoPoints'] + match['score_breakdown']['red']['teleopPoints'] + match['score_breakdown']['red']['foulPoints'] + match['score_breakdown']['red']['adjustPoints'])
                else:
                    auto_points.append(match['score_breakdown']['blue']['autoPoints'])
                    teleop_points.append(match['score_breakdown']['blue']['teleopPoints'])
                    match_scores.append(match['score_breakdown']['blue']['autoPoints'] + match['score_breakdown']['blue']['teleopPoints'] + match['score_breakdown']['blue']['foulPoints'] + match['score_breakdown']['blue']['adjustPoints'])
            average_auto_points = round(sum(auto_points) / len(auto_points), 2)
            average_teleop_points = round(sum(teleop_points) / len(teleop_points), 2)
            average_match_score = round(sum(match_scores) / len(match_scores), 2)
    except:
        pass

    return wins, losses, win_percentage, average_match_score, match_scores, average_auto_points, average_teleop_points, comp_levels

def getRankings(event_key):
    # Get the rankings for the event
    rankings = getTBA("event/" + event_key + "/rankings")
    rank_list = []
    team_list = []
    
    # Loop through each team and add the rank and team number to the lists
    for team in rankings['rankings']:
        rank_list.append(team['rank'])
        team_list.append(team['team_key'][3:])

    tuple_list = list(zip(rank_list, team_list))
    # Sort the tuple list by rank
    tuple_list = sorted(tuple_list, key=lambda k: k[0])

    return tuple_list

def returnRankings(event_key):
    # Return the rankings for the event
    rankings = getTBA("event/" + event_key + "/rankings")
    return rankings

def getTeamRank(team, event_key):
    # Get the rank of the team
    try:
        rankings = returnRankings(event_key)
        for teamy in rankings['rankings']:
            if teamy['team_key'][3:] == team:
                return teamy['rank']
    except:
        return 7777

def getTeamRecord(team, event_key):
    # Get the record of the team
    try:
        rankings = returnRankings(event_key)
        for rank in rankings['rankings']:
            if rank['team_key'][3:] == team:
                return rank['record']['wins'], rank['record']['losses'], rank['record']['ties']
    except:
        return 7777, 7777, 7777

def getTeamOPRS(team, event_key):
    # Get the OPRS of the team
    try:
        oprs = getTBA("event/" + event_key + "/oprs")
        return round(oprs['oprs']['frc' + team], 2)
    except:
        return 7777

def getTeamDPRS(team, event_key):
    # Get the DPRS of the team
    try:
        dprs = getTBA("event/" + event_key + "/oprs")
        return round(dprs['dprs']['frc' + team], 2)
    except:
        return 7777

def getTeamCCWM(team, event_key):
    # Get the CCWM of the team
    try:
        ccwms = getTBA("event/" + event_key + "/oprs")
        return round(ccwms['ccwms']['frc' + team], 2)
    except:
        return 7777

def getPlayoffAlliances(event_key):
    # Get the playoff alliances for the event
    playoff_alliances = getTBA("event/" + event_key + "/alliances")
    alliance_list = []
    for alliance in playoff_alliances:
        alliance_list.append(alliance['picks'])
    return alliance_list

# This function will be used to gather charge consistency data for a team.
def getChargeConsistency(position, match_key, alliance, times, xData, yData):
    # Red Alliance Charge Station Zone
    # 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3
    # Blue Alliance Charge Station Zone
    # 43.3 > xData[i] > 38.3 and 21.3 > yData[i] > 13.3

    # Autonomous charging will occur from times 0 to 15 seconds
    # Teleop charging will occur from times 15 to 135 seconds

    teleop_attempted_charge = False
    teleop_charged = False
    auto_attempted_charge = False
    auto_charged = False
    teleop_type_charge = 'None'
    auto_type_charge = 'None'
    total_charge_points = 0

    for i in range(len(times)):
        if alliance == 'red':
            if times[i] < 150:
                if 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3 and not auto_attempted_charge:
                    auto_attempted_charge = True
            else:
                if 16.1 > xData[i] > 11.1 and 21.3 > yData[i] > 13.3 and not teleop_attempted_charge:
                    teleop_attempted_charge = True
        else:
            if times[i] < 150:
                if 43.3 > xData[i] > 38.3 and 21.3 > yData[i] > 13.3 and not auto_attempted_charge:
                    auto_attempted_charge = True
            else:
                if 43.3 > xData[i] > 38.3 and 21.3 > yData[i] > 13.3 and not teleop_attempted_charge:
                    teleop_attempted_charge = True

    if alliance == 'red':
        # Check if the robot actually charged in teleop
        try:
            if teleop_attempted_charge or auto_attempted_charge:
                match_info = getTBA("match/" + match_key)
                score_breakdown = match_info["score_breakdown"]
                charging = score_breakdown['red'][f"endGameChargeStationRobot{position}"]
                if charging == "Docked" or charging == "Engaged":
                    teleop_charged = True
                    if charging == "Docked":
                        teleop_type_charge = 'Docked'
                    else:
                        teleop_type_charge = 'Engaged'

                # Check if the robot actually charged in auto
                charging = score_breakdown['red'][f"autoChargeStationRobot{position}"]
                if charging == "Docked" or charging == "Engaged":
                    auto_charged = True
                    if charging == "Docked":
                        auto_type_charge = 'Docked'
                    else:
                        auto_type_charge = 'Engaged'
        except:
            pass
    else:
        # Check if the robot actually charged in teleop
        try:
            if teleop_attempted_charge or auto_attempted_charge:
                match_info = getTBA("match/" + match_key)
                score_breakdown = match_info["score_breakdown"]
                charging = score_breakdown['blue'][f"endGameChargeStationRobot{position}"]
                if charging == "Docked" or charging == "Engaged":
                    teleop_charged = True
                    if charging == "Docked":
                        teleop_type_charge = 'Docked'
                    else:
                        teleop_type_charge = 'Engaged'

                # Check if the robot actually charged in auto
                charging = score_breakdown['blue'][f"autoChargeStationRobot{position}"]
                if charging == "Docked" or charging == "Engaged":
                    auto_charged = True
                    if charging == "Docked":
                        auto_type_charge = 'Docked'
                    else:
                        auto_type_charge = 'Engaged'
        except:
            pass

    return teleop_attempted_charge, teleop_charged, teleop_type_charge, auto_attempted_charge, auto_charged, auto_type_charge
    


# This function will use zone data to determine if a team is mostly defense or offense. This will be a prediction that is hopefully accurate.
def determineDefense(team, event_key, alliance, times, xData, yData):
    # Zones indicating when a robot is defending:
    
    # If the red alliance is in these zones, the robot is defending
    # Zone 1: x values: 16 to 27 y values: 0 to 8.5
    
    # If the blue alliance is in these zones, the robot is defending
    # Zone 1: x values: 27 to 38 y values: 0 to 8.5

    # If the time spent in the zone is greater than 50% of the match, the robot is mostly defense

    time_in_zone = 0
    for i in range(len(times)):
        if alliance == 'red':
            if 16 < xData[i] < 27 and 0 < yData[i] < 8.5:
                time_in_zone += 1
        elif alliance == 'blue':
            if 27 < xData[i] < 38 and 0 < yData[i] < 8.5:
                time_in_zone += 1

    return time_in_zone

# Utilize the determine defense function and the getTeamCCWM function to determine if a team is mostly defense or offense
def returnDefense(team, event_key, average_time_defense):
    ccwm = getTeamCCWM(team, event_key)
    could_defense = False
    likely_defense = False
    very_defense = False
    # Check if the average time the robot spends in a defense is greater than half the length of a match
    if (average_time_defense > ((150 - 150 * .1)) / 3) and ccwm < 0:
        likely_defense = True
        # Check if the team spends more than 1/2 of the match in a defense
        if average_time_defense > ((150 - (150 * .1)) / 2):
            very_defense = True
    if likely_defense == False and very_defense == False and getTeamCCWM(team, event_key) < 0:
        could_defense = True

    if likely_defense == True or very_defense == True:
        return True
    else:
        return False

def get_scoreBreakdown(match_key):
    try:
        match_info = getTBA("match/" + match_key)
        score_breakdown = match_info["score_breakdown"]
        return score_breakdown
    except:
        return None

def match_predictWinner(event_key, match_key):
    # First get all the teams in the match
    match_info = getTBA("match/" + match_key)
    red_teams = match_info["alliances"]["red"]["team_keys"]
    blue_teams = match_info["alliances"]["blue"]["team_keys"]

    # Format the team keys to only have the numbers.
    for i in range(len(red_teams)):
        red_teams[i] = (red_teams[i][3:])
    for i in range(len(blue_teams)):
        blue_teams[i] = (blue_teams[i][3:])

    # Get the oprs for each team
    red_oprs = []
    blue_oprs = []
    for team in red_teams:
        red_oprs.append(getTeamOPRS(team, event_key))
    for team in blue_teams:
        blue_oprs.append(getTeamOPRS(team, event_key))

    # Add up the oprs for each team
    red_opr = 0
    blue_opr = 0
    for opr in red_oprs:
        red_opr += opr
    for opr in blue_oprs:
        blue_opr += opr

    # Check which team has the higher opr and set winner to that alliance
    if red_opr > blue_opr:
        winner = 'Red Alliance'
    elif blue_opr > red_opr:
        winner = 'Blue Alliance'

    # Predict the score from each alliance 
    red_score = 0
    blue_score = 0
    for i in range(len(red_oprs)):
        red_score += red_oprs[i]
    for i in range(len(blue_oprs)):
        blue_score += blue_oprs[i]

    # Round the scores
    red_score = round(red_score)
    blue_score = round(blue_score)

    return winner, red_score, blue_score, red_teams, blue_teams, red_oprs, blue_oprs

def getRealMatchScore(match_key):
    score_breakdown = get_scoreBreakdown(match_key)
    red_score = score_breakdown['red']['totalPoints']
    blue_score = score_breakdown['blue']['totalPoints']
    return red_score, blue_score

def distanceFivePointMovingAverage(xData, yData):
    distanceWindows = []
    for i in range(5):
        distanceWindows.append(-7777)

    # Those were not real distances... To find distance we need two points, not just one set
    distances = []
    for i in range(len(xData) - 1):
        distances.append(math.sqrt((xData[i + 1] - xData[i])**2 + (yData[i + 1] - yData[i])**2))


    first_five_average = 0
    for i in range(5):
        first_five_average += distances[i]
    first_five_average = first_five_average / 5

    distanceWindows.append(first_five_average)

    # Starting_point 1 is really the second point in the list and ending point 5 is really the 6th point in the list
    starting_point = 1
    ending_point = 5
    
    # while ending_point < len(distances):
    #     next_five_window = 0
    #     for i in range(starting_point, ending_point + 1):
    #         next_five_window += distances[i]
    #     next_five_window = next_five_window / 5
    #     distanceWindows.append(next_five_window)
    #     starting_point += 1
    #     ending_point += 1

    # Re-written moving average calculation to reduce number of operations occuring.
    next_five_window = 0
    for i in range(starting_point, ending_point + 1):
        next_five_window += distances[i]
    average_over_window = next_five_window / 5
    distanceWindows.append(average_over_window)
    starting_point += 1
    ending_point += 1

    while ending_point < len(distances):
        average_over_window = 0
        next_five_window = next_five_window - distances[starting_point - 1] + distances[ending_point]
        average_over_window = next_five_window / 5
        distanceWindows.append(average_over_window)
        starting_point += 1
        ending_point += 1

    return distanceWindows

# Create a method to calculate the total distance traveled by a robot using a five point moving average
def totalDistanceTraveled(xData, yData):
    distanceWindows = distanceFivePointMovingAverage(xData, yData)
    distanceWindows = [0 if x == -7777 else x for x in distanceWindows]
    total_distance = 0
    for i in range(len(distanceWindows)):
        total_distance += distanceWindows[i]
    return total_distance

# Create a method to calculate the average speed of a robot using a five point moving average
def fivePointAverageVelocity(xData, yData, times):
    # Calculate the total distance traveled over a 5 point moving window
    distanceWindows = distanceFivePointMovingAverage(xData, yData)

    time_passed = 0.5

    distanceWindows = [0 if x == -7777 else x for x in distanceWindows]

    # Loop through the distanceWindows list and using a 5 point moving window, calculate the average velocity by adding the next 5 distances and dividing by time_passed
    average_velocity = []
    for i in range(len(distanceWindows)):
        if i < 5:
            average_velocity.append(-7777)
        else:
            average_velocity.append(sum(distanceWindows[i - 5:i]) / time_passed)

    average_velocity = [0 if x == -7777 else x for x in average_velocity]

    return average_velocity

# Create a method to calculate that returns the highest average velocity of a robot
def highestAverageVelocity(xData, yData, times):
    average_velocity = fivePointAverageVelocity(xData, yData, times)

    highest_velocities = []
    # Loop through the average_velocity list and append any values to highest_velocities that are greater than 95% of the other values
    for i in range(len(average_velocity)):
        if average_velocity[i] > 0.95 * max(average_velocity):
            highest_velocities.append(average_velocity[i])

    highest_average_velocity = sum(highest_velocities) / len(highest_velocities)
    return highest_average_velocity