import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
import traceback
from streamlit_player import st_player

# Google Analytics
import pathlib
from bs4 import BeautifulSoup
import logging
import shutil

# Data Visualization
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData, get_team_match_videos, team_performance, average_speed, getRankings, getTeamCCWM, getTeamDPRS, getTeamOPRS, getTeamRank, getTeamRecord, getPlayoffAlliances, determineDefense, getChargeConsistency, average_speed_topPercentile, max_speed, get_scoreBreakdown, match_predictWinner, getRealMatchScore, distanceFivePointMovingAverage, highestAverageVelocity, totalDistanceTraveled, fivePointAverageVelocity  

# Google Analytics


def inject_ga():
    GA_ID = "google_analytics"

    GA_JS = """
   <!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-NH20RWNP3G"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-NH20RWNP3G');
</script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    logging.info(f'editing {index_path}')
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)
        else:
            shutil.copy(index_path, bck_index)
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)


inject_ga()

#team = 564
teams = [564, 870, 263, 514, 527, 694]

# Create a streamlit select box for the user to select the team they want to see
#team = st.selectbox("Select a team", teams)

team = teams[0]
year = 2024

formattedNames = []
namesList = get_events(year)
for name in namesList:
    formatted = f"{name[0]}, ({name[1]})"
    formattedNames.append(formatted)

formattedNames.remove("Finger Lakes Regional, (2024nyro)")
formattedNames.insert(0, "Finger Lakes Regional, (2024nyro)")
        
event = st.selectbox("Select an event", formattedNames)
event_key = event[event.index('('):]
event_key = event_key[1:-1]

team_numbers = []

get_teams = get_events_teams(event_key)
for team in get_teams:
    team = team[team.index(','):]
    team = team[2:]

    while len(team) > 4:
        team = team[team.index(','):]
        team = team[2:]

    team_numbers.append(team)

teams = st.selectbox("Select a team", team_numbers)
team = teams
#team = teams[teams.index(','):]
#team = team[2:]

data_selection_choices = ["Team-Performance-Stats", "Match-Videos", "Event-Stats", "Match-Predictions"]

data_selector = st.selectbox("Select a type of Data to search for", data_selection_choices)

if data_selector == "Team-Performance-Stats":
    with st.spinner(f"The performance statistics of team {team} are loading"):
        performance_stats = team_performance(team, event_key)

        wins = performance_stats[0]
        losses = performance_stats[1]
        win_percentage = performance_stats[2]
        avg_match_score = performance_stats[3]
        match_scores = performance_stats[4]
        avg_auto_points = performance_stats[5]
        avg_teleop_points = performance_stats[6]
        comp_levels = performance_stats[7]

        display = True

        if 0 in {win_percentage, avg_match_score}:
            st.warning("It appears that data for this teams matches has not been added yet... Has this team played a match?", icon="⚠️")
            display = False

        if display:

            st.write(f"# :violet[The following are the performance statistics for team {team} at the {event} event.]")
            
            st.write(f"## :green[Wins: {wins}]")
            st.write(f"## :red[Losses: {losses}]")
            st.write(f"## :orange[Win Percentage: {win_percentage}%]")
            st.write(f"## :violet[Average Match Score: {avg_match_score}]")
            st.write(f"## :violet[Average Auto Points: {avg_auto_points}]")
            st.write(f"## :green[Average Teleop Points: {avg_teleop_points}]")
    
            match_numbers = []
            matches = competition_match_data(team, event_key)
            # Sort the matches from earliest to latest
            matches.sort(key=lambda x: x[1])
            for match in matches:
                match_numbers.append(match[1])
    
            while (len(match_numbers) > len(match_scores)):
                match_numbers.pop(-1)
            
            comp_count = 0
            tab_labels = []
            for match in match_numbers:
                label = f"{comp_levels[comp_count].upper()} Match {match}"
                tab_labels.append(label)
                comp_count += 1
    
            count = 0
            # Create a streamlit tab selector for the user to select the match and then view the match score for that match as well as a st.metric representing the percent above or below the average match score
            for tab in st.tabs(tab_labels):
                with tab:
                    match_number = match_numbers[count]
                    match_score = match_scores[count]
                    st.write(f"## :green[Team {team}'s alliance score for match :orange[{match_number}] is ] :orange[{match_score}]")
                    if match_score > avg_match_score:
                        st.metric(label="Match Score", value=match_score, delta=f"{round(match_score - avg_match_score, 2)}% Above the teams average match score")
                    else:
                        st.metric(label="Match Score", value=match_score, delta=f"{-round(avg_match_score - match_score, 2)}% Below the teams average match score")
                count += 1

        # Add a streamlit info box to the bottom of the page mentioning that the data is provided by Longwood Robotics Team 564
        st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Match-Videos":
    with st.spinner(f"The videos for team {team} are loading!"):
        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])
        videos = []
        for match in matches:
            match_key = str(match[5])
            video = get_team_match_videos(team, match_key)
            videos.append(video)
        display = True
        if len(videos) == 0:
            st.warning("It appears that data for this teams matches has not been added yet... Has this team played a match?", icon="⚠️")
            display = False
        if display:
            st.write(f"# :orange[The following videos are for team {team} at the {event} event.]")
            for video in videos:
                try:
                    st_player(f"https://youtu.be/{video}")
                except:
                    pass

        # Add a streamlit info box to the bottom of the page mentioning that the data is provided by Longwood Robotics Team 564
        st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Cycle-Data":
    with st.spinner("Your data is loading!"):
        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])
        
        num_cycles_list = []
        avg_time_cross_list = []
        display = True
        distance_travelled_list = []
        
        try:
            for match in matches:
                try:
                    # Check if the match is a qualification match (qm), quarterfinal (qf), semifinal (sf), or final (f)
                    if match[4] == 'qm':
                        match_type = 'Qualification'
                        times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
                    elif 'qf' in match[4]:
                        match_type = 'Quarterfinal'
                        times, xData, yData = zebra_data_quarterfinals_pull(match[0], match[1], match[2], match[3], match[4])
                    elif 'sf' in match[4]:
                        match_type = 'Semifinal'
                        times, xData, yData = zebra_data_semifinals_pull(match[0], match[1], match[2], match[3], match[4])
                    elif 'f' in match[4] and 'qf' not in match[4] and 'sf' not in match[4]:
                        match_type = 'Final'
                        times, xData, yData = zebra_data_finals_pull(match[0], match[1], match[2], match[3], match[4])
        
                    match_key = str(match[5])
                    cycle_data = get_cycleData(match_key, match[2], times, xData, yData)
                    num_cycles_list.append(cycle_data[1])
                    if cycle_data[2] != 7777:
                        distance_travelled_list.append(cycle_data[2])
                    else:
                        pass
                    if cycle_data[0] != 7777:
                        avg_time_cross_list.append(cycle_data[0])
                    else:
                        pass

                except:
                    pass

            try:
                total_avg_distance = round(sum(distance_travelled_list) / len(distance_travelled_list), 2)
                total_avg_cycles = round(sum(num_cycles_list) / len(num_cycles_list), 2)
                total_avg_time_cycle = round(sum(avg_time_cross_list) / len(avg_time_cross_list), 2)
            except:
                st.warning("It appears that data for this teams matches has not been added yet... Has this team played a match?", icon="⚠️")
                display = False
                
        except Exception as e:
            st.write(e)
            #st.write("# :red[It appears to be possible that the team you are trying to search for Data for does not participate in using the Zebra MotionWorks trackers.]")
            display = False

    if display:

        st.info("A *cycle* is completed when a team's robot travels to their alliance's correlating loading zone, and back into their community.", icon="ℹ️")
        
        st.write(f"Team {team} completes an average of :orange[**{total_avg_cycles} cycles**] per match.")
        st.write(f"The average time it takes the team to complete a cycle is: :orange[**{total_avg_time_cycle} seconds**].")
        st.write(f"The average distance travelled by the team during a cycle is: :orange[**{total_avg_distance} feet**].")

        comp_levels = []
        for match in matches:
            comp_levels.append(match[4])

        match_numbers = []
        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])
        for match in matches:
            match_numbers.append(match[1])

        working_matches = []
        for match in matches:
            if get_scoreBreakdown(match[5]) != None:
                working_matches.append(match)

        working_numbers = []
        for match in working_matches:
            working_numbers.append(match[1])

        comp_count = 0
        tab_labels = []
        for match in working_numbers:
            label = f"{comp_levels[comp_count].upper()} Match {match}"
            tab_labels.append(label)
            comp_count += 1
    
        count = 0
        # Create a streamlit tab selector for the user to select the match and then view the match score for that match as well as a st.metric representing the percent above or below the average match score
        for tab in st.tabs(tab_labels):
            with tab:
                try:
                    # Display the average distance travelled for this match
                    st.metric(label="Average Distance Travelled", value=f"{round(distance_travelled_list[count], 2)} feet", delta=f"{-1 * round((distance_travelled_list[count] - total_avg_distance), 2)} feet")
                    # Display the average number of cycles for this match
                    st.metric(label="Average Number of Cycles", value=f"{num_cycles_list[count]} cycles", delta=f"{round((num_cycles_list[count] - total_avg_cycles), 2)} cycles")
                    # Display the average time to complete a cycle for this match
                    st.metric(label="Average Time to Complete a Cycle", value=f"{round(avg_time_cross_list[count], 2)} seconds", delta=f"{-1 * round((avg_time_cross_list[count] - total_avg_time_cycle), 2)} seconds")
                    count += 1
                except:
                    st.warning("It appears that distance travelled data for this match is not currently working. Please try again later.", icon="⚠️")

        # Display a fancy plotly graph to analyze the data
        #fig = go.Figure()
        #fig.add_trace(go.Scatter(x=matches, y=num_cycles_list, mode='lines+markers', name='Number of Cycles'))
        #fig.add_trace(go.Scatter(x=matches, y=avg_time_cross_list, mode='lines+markers', name='Average Time to Complete a Cycle'))
        #fig.update_layout(title=f"Team {team}'s Cycle Data", xaxis_title="Match Number", yaxis_title="Number of Cycles/Average Time to Complete a Cycle")
        #st.plotly_chart(fig)

        match_nums = []
        for match in matches:
            # Append the match comp level and match number to the list
            match_nums.append(f"{match[4].upper()} {match[1]}")

        #Sort the match_nums list by QM matches first, then SF, then QF, then F
        # Correlate QM to 1, SF to 2, QF to 3, and F to 4
        match_nums.sort(key=lambda x: (1 if 'QM' in x else 2 if 'SF' in x else 3 if 'QF' in x else 4 if 'F' in x else 5))

        # Do the same thing as above but clean up the x-axis
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=match_nums, y=num_cycles_list, mode='lines+markers', name='Number of Cycles'))
        fig.add_trace(go.Scatter(x=match_nums, y=avg_time_cross_list, mode='lines+markers', name='Average Time to Complete a Cycle'))
        fig.update_layout(title=f"Team {team}'s Cycle Data", xaxis_title="Match Number", yaxis_title="Number of Cycles/Average Time to Complete a Cycle")
        # List the match numbers in the x-axis
        fig.update_xaxes(tickvals=match_nums)
        st.plotly_chart(fig)

        st.warning("All data shown is obtained from **Zebra MotionWorks** data through TheBlueAlliance API.", icon="⚠️")

        # Add an info box to give credit
        st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Robot-Stats":
    # The first robot statistic will be the average speed of the robot.
    # To get the average speed we will use the zebra_speed function

    avg_speed_list = []
    avg_speed_topPerentile_list = []
    max_speeds_list = []

    times_in_defense_list = []

    # Get the average speed for the selected team by using the average_speed function
    matches = competition_match_data(team, event_key)
    for match in matches:
        try:
            # Check if the match is a qualification match (qm), quarterfinal (qf), semifinal (sf), or final (f)
            if match[4] == 'qm':
                match_type = 'Qualification'
                times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
            elif 'qf' in match[4]:
                match_type = 'Quarterfinal'
                times, xData, yData = zebra_data_quarterfinals_pull(match[0], match[1], match[2], match[3], match[4])
            elif 'sf' in match[4]:
                match_type = 'Semifinal'
                times, xData, yData = zebra_data_semifinals_pull(match[0], match[1], match[2], match[3], match[4])
            elif 'f' in match[4] and 'qf' not in match[4] and 'sf' not in match[4]:
                match_type = 'Final'
                times, xData, yData = zebra_data_finals_pull(match[0], match[1], match[2], match[3], match[4])
            # Get the average speed of the robot
            speed = average_speed(times, xData, yData)
            avg_speed_list.append(speed)
            topSpeeds = average_speed_topPercentile(times, xData, yData)
            avg_speed_topPerentile_list.append(topSpeeds)
            max_speed = max_speed(times, xData, yData)
            max_speeds_list.append(max_speed)
            time_defense = determineDefense(team, event_key, match[2], times, xData, yData)
            times_in_defense_list.append(time_defense)

        except:
            pass

    # While there are still 7777's in the list, remove them
    while 7777 in avg_speed_list:
        avg_speed_list.remove(7777)
    # Get the average speed of the robot
    average_speed = round(sum(avg_speed_list) / len(avg_speed_list), 2)

    # Display the average speed of the robot
    st.write(f"Team {team} has an average speed of :orange[**{average_speed} ft/s**]")

    # While there are still 7777's in the list, remove them
    while 7777 in avg_speed_topPerentile_list:
        avg_speed_topPerentile_list.remove(7777)
    
    # Get the average speed of the robot
    average_speed_topPercentile = round(sum(avg_speed_topPerentile_list) / len(avg_speed_topPerentile_list), 2)

    # Add an st.info blurb to explain that we use a top average speed to account for time sitting still in autonomous and charging
    st.info("We use a top average speed to account for time sitting still in autonomous and charging, aswell as while placing cones and cubes.", icon="ℹ️")

    # Display the average speed of the robot saying Team {team} has a top average speed of {average_speed_topPercentile} ft/s
    st.write(f"Team {team} has a top average speed of :orange[**{average_speed_topPercentile} ft/s**]")

    max_speed = max(max_speeds_list)
    max_speed = round(max_speed, 2)

    # Display the max speed of the max speeds list
    st.write(f"Team {team} has a maximum in-match viewed speed of :orange[**{max_speed} ft/s**]")

    # Get the average time the robot spends in a defense
    average_time_defense = round(sum(times_in_defense_list) / len(times_in_defense_list), 2)

    could_defense = False
    likely_defense = False
    very_defense = False
    # Check if the average time the robot spends in a defense is greater than half the length of a match
    if average_time_defense > ((len(times)/10 - (len(times)/10 * .1)) / 3) and getTeamCCWM(team, event_key) < 0:
        likely_defense = True
        # Check if the team spends more than 1/2 of the match in a defense
        if average_time_defense > ((len(times)/10 - (len(times)/10 * .1)) / 2):
            very_defense = True
    if likely_defense == False and very_defense == False and getTeamCCWM(team, event_key) < 0:
        could_defense = True

    # Display the average time the robot spends in a defense
    st.write(f"Team {team} spends an average of :orange[**{average_time_defense} seconds**] playing defense.")

    # Display our prediction of whether the robot is a defense robot or not
    if very_defense:
        st.write(f"Using our algorithm, we predict that Team {team} is :orange[**a very defensive robot**].")
        st.warning("This is not a guarantee that the robot is a defensive robot, but it is a good indicator that it is a defensive robot.", icon="⚠️")
    elif likely_defense:
        st.write(f"Using our algorithm, we predict that Team {team} is :green[**likely**] to  be :orange[**a defensive robot**].")
        st.warning("This is not a guarantee that the robot is a defensive robot, but it is a good indicator that it is a defensive robot.", icon="⚠️")
    elif could_defense:
        st.write(f"Using our algorithm, we predict that Team {team} :green[**could**] be :orange[**a defensive robot**].")
        st.warning("This is not a guarantee that the robot is a defensive robot, but it is a good indicator that it is a defensive robot.", icon="⚠️")
    else:
        st.write(f"Using our algorithm, we predict that Team {team} is :orange[**not a defensive robot**].")
        st.warning("This is not a guarantee that the robot is not a defensive robot, but it is a good indicator that it is not a defensive robot.", icon="⚠️")

    # Display a pie chart of the average time the robot spends in defense zones to represent our prediction
    fig = go.Figure(data=[go.Pie(labels=['Time in Defense Zones (seconds)', 'Time Not in Defense Zones (seconds)'], values=[average_time_defense, (len(times)/10 - (len(times)/10 * .1)) - average_time_defense])])
    fig.update_layout(title=f"Team {team}'s Average Time in Defense Zones (% of match)")
    st.plotly_chart(fig)

    st.warning("All data shown is obtained from **Zebra MotionWorks** data through TheBlueAlliance API.", icon="⚠️")

    # Add an info box to give credit
    st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Charge-Data":

    st.warning("This data can take a while to load due to the large quantity and numerous calculations. Please be patient.", icon="⚠️")
    with st.spinner("Loading..."):

        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest.
        match_sort_items = []
        for match in matches:
            # Trim match[5] by removing the _ and everything before it
            match_sort_items.append(match[5].split('_')[1])
        # Sort the match_sort_items list by qm first, then qf, then sf, then f
        match_sort_items.sort(key=lambda x: (1 if 'qm' in x else 2 if 'sf' in x else 3 if 'qf' in x else 4 if 'f' in x else 5))

        teleop_attempted_charges = []
        teleop_successful_charges = []
        teleop_charge_types = []
        autonomous_attempted_charges = []
        autonomous_successful_charges = []
        autonomous_charge_types = []

        try:

            matches = competition_match_data(team, event_key)
            # Sort the matches list by comparing the match_sort_items list to the endings of the match keys
            matches.sort(key=lambda x: match_sort_items.index(x[5].split('_')[1]))
            
            # Remove any matches in the matches list that are not qualification matches
            for match in matches:
                if match[4] != 'qm':
                    matches.remove(match)
            # Check again
            for match in matches:
                if match[4] != 'qm':
                    matches.remove(match)

            for match in matches:
                # Check if the match is a qualification match (qm), quarterfinal (qf), semifinal (sf), or final (f)
                if match[4] == 'qm':
                    match_type = 'Qualification'
                    times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
                elif 'qf' in match[4]:
                    match_type = 'Quarterfinal'
                    times, xData, yData = zebra_data_quarterfinals_pull(match[0], match[1], match[2], match[3], match[4])
                elif 'sf' in match[4]:
                    match_type = 'Semifinal'
                    times, xData, yData = zebra_data_semifinals_pull(match[0], match[1], match[2], match[3], match[4])
                elif 'f' in match[4] and 'qf' not in match[4] and 'sf' not in match[4]:
                    match_type = 'Final'
                    times, xData, yData = zebra_data_finals_pull(match[0], match[1], match[2], match[3], match[4])

                match_key = str(match[5])
                position = match[3]
                color = match[2]

                charge_data = getChargeConsistency(position, match_key, color, times, xData, yData)
                teleop_attempted_charges.append(charge_data[0])
                teleop_successful_charges.append(charge_data[1])
                teleop_charge_types.append(charge_data[2])
                autonomous_attempted_charges.append(charge_data[3])
                autonomous_successful_charges.append(charge_data[4])
                autonomous_charge_types.append(charge_data[5])
        except:
            pass

        total_attempted_teleop_charges_num = 0
        total_successful_teleop_charges_num = 0
        total_attempted_autonomous_charges_num = 0
        total_successful_autonomous_charges_num = 0

        for charge in teleop_attempted_charges:
            if charge == True:
                total_attempted_teleop_charges_num += 1
        for charge in teleop_successful_charges:
            if charge == True:
                total_successful_teleop_charges_num += 1
        for charge in autonomous_attempted_charges:
            if charge == True:
                total_attempted_autonomous_charges_num += 1
        for charge in autonomous_successful_charges:
            if charge == True:
                total_successful_autonomous_charges_num += 1

        check_for_data = True

        # Check if total attempted teleop or autonomous charges is 0
        if total_attempted_teleop_charges_num == 0 or total_attempted_autonomous_charges_num == 0:
            check_for_data = False
            # Send a warning saying that this team has not attempted to charge.
            st.warning(f"Team {team} has no charge data. This could be due to no attempt at charging.", icon="⚠️")

        if check_for_data:
            st.title(f"Charge Data for Team {team}")

            teleop_charge_success_rate = round((total_successful_teleop_charges_num / total_attempted_teleop_charges_num) * 100, 2)
            autonomous_charge_success_rate = round((total_successful_autonomous_charges_num / total_attempted_autonomous_charges_num) * 100, 2)

            st.write(f"**Teleop Charge Success Rate:** {teleop_charge_success_rate} %")
            st.write(f"**Autonomous Charge Success Rate:** {autonomous_charge_success_rate} %")

            # Display a chart representing teleop charge success rate, autonomous charge success rate
            #fig = go.Figure(data=[go.Pie(labels=['Teleop Charge Success Rate', 'Autonomous Charge Success Rate'], values=[teleop_charge_success_rate, autonomous_charge_success_rate])])
            #fig.update_layout(title=f"Team {team}'s Charge Success Rate")
            #st.plotly_chart(fig)

            # Display a chart representing the total number of attempted charges in either teleop or autonomous and the total number of successful charges in either teleop or autonomous
            total_charge_successes = total_successful_teleop_charges_num + total_successful_autonomous_charges_num
            total_charge_attempts = total_attempted_teleop_charges_num + total_attempted_autonomous_charges_num
            total_charge_success_rate = round((total_charge_successes / total_charge_attempts) * 100, 2)
            fig = go.Figure(data=[go.Pie(labels=['Total Charge Success Rate', 'Total Charge Failure Rate'], values=[total_charge_success_rate, 100 - total_charge_success_rate])])
            fig.update_layout(title=f"Team {team}'s Total Charge Success Rate")
            st.plotly_chart(fig)

            st.write(f"**Total Attempted Teleop Charges:** {total_attempted_teleop_charges_num}")
            st.write(f"**Total Successful Teleop Charges:** {total_successful_teleop_charges_num}")
            st.write(f"**Total Attempted Autonomous Charges:** {total_attempted_autonomous_charges_num}")
            st.write(f"**Total Successful Autonomous Charges:** {total_successful_autonomous_charges_num}")

            st.warning("All data shown is obtained from **Zebra Motionworks** data through TheBlueAlliance API.", icon="⚠️")
    
        # Add an info box to give credit
        st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Event-Stats":
    # Display the event statistics.
    st.title(f"Event Statistics for {event_key}")

    if st.checkbox("Show Event Rankings"):
        # Utilize the getRankings/getTeamRank/getTeamRecord/getPlayoffAlliances/getTeamOPRS/getTeamDRPS/getTeamCCWMs functions to display the event statistics.
        rankings = getRankings(event_key)
        # Create a leaderboard using the rankings and matplotlib.
        # Convert the rankings to a dictionary.
        rankings_dict = {}
        for teamy in rankings:
            rankings_dict[teamy[0]] = teamy[1]
        plotly_fig = go.Figure(data=[go.Table(header=dict(values=['Rank', 'Team']), cells=dict(values=[list(rankings_dict.keys()), list(rankings_dict.values())]))])
        # Resize the plotly figure.
        plotly_fig.update_layout(width=1000, height=1000)
        # Center the plotly figure.
        plotly_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(plotly_fig)

    team_rank = getTeamRank(team, event_key)
    # Check if team_rank is 7777
    if team_rank == 7777:
        st.write(f":red[The team rank for team {team} is not currently available.]")
    else:
        st.write(f"Team Rank: \n{team_rank}")

    team_record = getTeamRecord(team, event_key)
    # Check if team_record is 7777, 7777, 7777
    if team_record == (7777, 7777, 7777):
        st.write(f":red[The team record for team {team} is not currently available.]")
    else:
        # Format the team record like wins-losses-ties.
        team_record = f"{team_record[0]}-{team_record[1]}-{team_record[2]}"
        st.write(f"Team Record: \n{team_record}")

    st.info("OPR stands for Offensive Power Rating, which is a system to attempt to deduce the average point contribution of a team to an alliance.", icon="ℹ️")
    team_oprs = getTeamOPRS(team, event_key)
    # Check if team_oprs is 7777
    if team_oprs == 7777:
        st.write(f":red[The team OPRs for team {team} are not currently available.]")
    else:
        st.write(f"Team OPRs: \n{team_oprs}")

    st.info("DPR stands for Defensive Power Rating, which is a system to attempt to deduce the average point reduction of a team to an alliance.", icon="ℹ️")
    team_drps = getTeamDPRS(team, event_key)
    # Check if team_drps is 7777
    if team_drps == 7777:
        st.write(f":red[The team DPRs for team {team} are not currently available.]")
    else:
        st.write(f"Team DPRs: \n{team_drps}")

    st.info("CCWM stands for Calculated Contribution to Winning Margin, which is a metric that combines OPR and DPR to estimate how much a team contributes to the win margin of a match.", icon="ℹ️")
    team_ccwms = getTeamCCWM(team, event_key)
    # Check if team_ccwms is 7777
    if team_ccwms == 7777:
        st.write(f":red[The team CCWMs for team {team} are not currently available.]")
    else:
        st.write(f"Team CCWMs: \n{team_ccwms}")

    playoff_alliances = getPlayoffAlliances(event_key)
    # Check if playoff_alliances is 7777
    if playoff_alliances == 7777:
        st.write(f":red[The playoff alliances for event {event_key} are not currently available.]")
    else:
        # Convert the playoff alliances to a dictionary.
        playoff_alliances_dict = {}
        alliance_number = 1
        for alliance in playoff_alliances:
            # Format the alliance teams into a string.
            alliance = ", ".join(alliance)
            # Remove the "frc" from the alliance teams.
            alliance = alliance.replace("frc", "")
            playoff_alliances_dict[f"Alliance {alliance_number}"] = alliance
            alliance_number += 1
        # Format the playoff alliances into a table using plotly.
        plotly_fig = go.Figure(data=[go.Table(header=dict(values=['Alliance', 'Teams']), cells=dict(values=[list(playoff_alliances_dict.keys()), list(playoff_alliances_dict.values())]))])
        # Get rid of margins
        plotly_fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(plotly_fig)

    # Add an info box to give credit
    st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Match-Predictions":
    # Display the match predictions.
    st.title(f"Match Predictions for {event_key}")

    with st.spinner(f"The match predictions for team {team} are loading!"):

        # Get the match data for the team.
        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])

        # Create tabs for all the matches for the team
        comp_levels = []
        for match in matches:
            comp_levels.append(match[4])

        match_numbers = []
        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])
        for match in matches:
            match_numbers.append(match[1])

        comp_count = 0
        tab_labels = []
        for match in match_numbers:
            label = f"{comp_levels[comp_count].upper()} Match {match}"
            tab_labels.append(label)
            comp_count += 1
        
        count = 0
        # Create a streamlit tab selector for the user to select the match and then view the match score for that match as well as a st.metric representing the percent above or below the average match score
        for tab in st.tabs(tab_labels):
            with tab:
                # Get the match predictions for the match using the match_predictWinner function
                match_predictions = match_predictWinner(event_key, matches[count][5])
                winner = match_predictions[0]
                red_score = match_predictions[1]
                blue_score = match_predictions[2]
                red_teams = match_predictions[3]
                blue_teams = match_predictions[4]
                red_oprs = match_predictions[5]
                blue_oprs = match_predictions[6]

                # Find which alliance the team is on
                if team in red_teams:
                    team_alliance = "Red Alliance"
                elif team in blue_teams:
                    team_alliance = "Blue Alliance"

                # Display the predicted winner as well as the predicted match score
                if winner == "Red Alliance":
                    st.write(f"Predicted Winner: :red[**{winner}**]")
                elif winner == "Blue Alliance":
                    st.write(f"Predicted Winner: :blue[**{winner}**]")

                st.write(f"Predicted Match Score: \n:red[**{red_score}**] - :blue[**{blue_score}**]")

                # Check if the team is on the predicted winner
                if winner == team_alliance:
                    st.success(f":white_check_mark: Team {team} is on the predicted winners alliance!")
                else:
                    st.error(f":x: Team {team} is not on the predicted winners alliance!")

                # Format the team lists to a string
                red_teams = ", ".join(red_teams)
                blue_teams = ", ".join(blue_teams)

                # Display the participating teams on each alliance
                st.write(f"Red Alliance Teams: \n:red[**{red_teams}**]")
                st.write(f"Blue Alliance Teams: \n:blue[**{blue_teams}**]")

                # Round each OPR
                red_oprs = [round(opr) for opr in red_oprs]
                blue_oprs = [round(opr) for opr in blue_oprs]

                # Create a seperate table for each alliance which shows the team number and their opr contribution using pandas dataframes
                red_oprs_df = pd.DataFrame(list(zip(red_teams.split(", "), red_oprs)), columns =['Team', 'OPR'])
                blue_oprs_df = pd.DataFrame(list(zip(blue_teams.split(", "), blue_oprs)), columns =['Team', 'OPR'])

                # Add 1 to the index column
                red_oprs_df.index += 1
                blue_oprs_df.index += 1

                st.table(red_oprs_df)
                st.table(blue_oprs_df)

                # Warn that the match predictions are not a guarantee
                st.warning("The match predictions are not a guarantee and are only predictions based on the data available.", icon="⚠️")

                count += 1

        # Add an info box to give credit
        st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")

if data_selector == "Motion-Stats":

    matches = competition_match_data(team, event_key)
    # Sort the matches from earliest to latest
    matches.sort(key=lambda x: x[1])

    # Create tabs for all the matches for the team
    comp_levels = []
    for match in matches:
        comp_levels.append(match[4])

    match_numbers = []
    matches = competition_match_data(team, event_key)
    # Sort the matches from earliest to latest
    matches.sort(key=lambda x: x[1])
    for match in matches:
        match_numbers.append(match[1])

    comp_count = 0
    tab_labels = []
    for match in match_numbers:
        label = f"{comp_levels[comp_count].upper()} Match {match}"
        tab_labels.append(label)
        comp_count += 1

    count = 0
    match_count = 0
    for tab in st.tabs(tab_labels):
        with tab:

            matches = competition_match_data(team, event_key)
            # Sort the matches from earliest to latest
            matches.sort(key=lambda x: x[1])
            match = matches[match_count]

            try: 
                # Check if the match is a qualification match (qm), quarterfinal (qf), semifinal (sf), or final (f)
                if match[4] == 'qm':
                    match_type = 'Qualification'
                    times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
                elif 'qf' in match[4]:
                    match_type = 'Quarterfinal'
                    times, xData, yData = zebra_data_quarterfinals_pull(match[0], match[1], match[2], match[3], match[4])
                elif 'sf' in match[4]:
                    match_type = 'Semifinal'
                    times, xData, yData = zebra_data_semifinals_pull(match[0], match[1], match[2], match[3], match[4])
                elif 'f' in match[4] and 'qf' not in match[4] and 'sf' not in match[4]:
                    match_type = 'Final'
                    times, xData, yData = zebra_data_finals_pull(match[0], match[1], match[2], match[3], match[4])

                average_distances = distanceFivePointMovingAverage(xData, yData)
                total_distance = totalDistanceTraveled(xData, yData)
                average_velocities = fivePointAverageVelocity(xData, yData, times)
                max_average_velocity = highestAverageVelocity(xData, yData, times)
                # Check for any values -7777 and replace them with 0
                average_distances = [0 if x == -7777 else x for x in average_distances]

                # Write the total distance traveled and the highest average velocity
                st.write(f"Total Distance Traveled: :red[**{round(total_distance ,2)}**] feet")
                st.write(f"Highest Average Velocity: :red[**{round(max_average_velocity, 2)}**] feet/second")

                # We want to create a graph with the following guidelines:
                # 1. the y-axis is labeled "Cumulative Percent" and ranges from 0 - 100 with a step size of 10
                # 2. the x-axis is labeled FT / S and ranges from 2.5 to 17.5 with a step size of .5
                # 3. the graph is titled "% of Measurments at or below Velocity X, but above 2 ft/s"
                # 4. The graph is a bar graph
                # 5. The graph highlights the roughly 90% bar with green, the roughly 95% bar with yellow, and the roughly 99% bar with red
                # Those are all of the graph requirements. Now we need to create the data for the graph.

                # Create the bins
                bins = []
                for i in range(5, 35):
                    bins.append(i/2)

                # Find the percentage of measurements at or below each velocity correlating to each bin
                # Regardless of whether a measurement is included in a previous bin, also include it in any other bins it qualifies for
                # Ex: If a measurement is 3.5 ft/s, it will be included in the 5 ft/s or less bin, the 4 ft/s or less bin, and the 17.5 ft/s or less bin
                percentages = []
                for i in range(len(bins)):
                    count = 0
                    for j in range(len(average_velocities)):
                        if average_velocities[j] <= bins[i]:
                            count += 1
                    percentages.append((count/len(average_velocities)) * 100)

                # Create a dictionary with the bins as the keys and the percentages as the values
                data = {'Velocity (ft/s)': bins, 'Cumulative Percent': percentages}

                # Create a dataframe from the dictionary
                df = pd.DataFrame(data)

                # Error control
                st.set_option('deprecation.showPyplotGlobalUse', False)

                # Plot the dataframe as a bar graph but make sure we stick to the graph requirements

                # Find the bars closest to 90, 95, and 99 percent and color them accordingly.
                 
                # Find the x value of the bar that is closest to 90%
                ninety_index = 0
                for i in range(len(df['Cumulative Percent'])):
                    if df['Cumulative Percent'][i] >= 90:
                        ninety_index = i
                        break
                # Find the x value of the bar that is closest to 95%
                ninety_five_index = 0
                for i in range(len(df['Cumulative Percent'])):
                    if df['Cumulative Percent'][i] >= 95:
                        ninety_five_index = i
                        break
                # Find the x value of the bar that is closest to 99%
                ninety_nine_index = 0
                for i in range(len(df['Cumulative Percent'])):
                    if df['Cumulative Percent'][i] >= 99:
                        ninety_nine_index = i
                        break
                
                # Create a list of colors
                colors = []
                for i in range(len(df['Cumulative Percent'])):
                    if i == ninety_index:
                        colors.append('green')
                    elif i == ninety_five_index:
                        colors.append('yellow')
                    elif i == ninety_nine_index:
                        colors.append('red')
                    else:
                        colors.append('blue')

                # Plot the dataframe as a bar graph
                df.plot.bar(x='Velocity (ft/s)', y='Cumulative Percent', title='% of Measurements at or below Velocity X, but above 2 ft/s', color=colors, ylim=(0, 100), yticks=np.arange(0, 101, 10), figsize=(10, 5))

                # Make sure the y-label is "Cumulative Percent" (The y-label was not appearing for some reason)
                plt.ylabel('Cumulative Percent')

                # Put the title higher so it does not overlap with our text labels
                plt.title('% of Measurements at or below Velocity X, but above 2 ft/s', y=1.05)

                # At the bars representing the approximate 90%, 95%, and 99% values, add text labels with the exact percentages above the bars
                plt.text(ninety_index, df['Cumulative Percent'][ninety_index] + 1, str(round(df['Cumulative Percent'][ninety_index], 2)) + '%', ha='center')
                plt.text(ninety_five_index, df['Cumulative Percent'][ninety_five_index] + 1, str(round(df['Cumulative Percent'][ninety_five_index], 2)) + '%', ha='center')
                plt.text(ninety_nine_index, df['Cumulative Percent'][ninety_nine_index] + 1, str(round(df['Cumulative Percent'][ninety_nine_index], 2)) + '%', ha='center')

                # Remove the legend
                plt.legend().remove()
                # Add horizontal grid lines only
                plt.grid(b=True, which='major', axis='y', color='grey', linestyle='-', alpha=0.5)

                # Create a line of best fit for the graph
                line = np.polyfit(df['Velocity (ft/s)'], df['Cumulative Percent'], 1)

                # Plot the line but make sure it is unobtrusive and does not overlap any text by using the -- text style.
                plt.plot(df['Velocity (ft/s)'], line[0] * df['Velocity (ft/s)'] + line[1], color='black', linestyle='--', linewidth=1)

                # Add text labels to the line of best fit
                plt.text(0, 99, 'Acceleration: ' + str(round(line[0], 2)) + ' ft/s^2', ha='left', va='top')

                st.pyplot()
                    

            except Exception as e:
                st.error(f"Something went wrong! It is possible that MotionWorks data for this match was not collected properly!")

            match_count += 1

    # Add a warning mentioning that the data is generated using MotionWorks data
    st.warning("All data shown is obtained from **Zebra MotionWorks** data through TheBlueAlliance API.", icon="⚠️")

    # Add an info box to give credit
    st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")