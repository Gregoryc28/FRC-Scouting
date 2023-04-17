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

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData, get_team_match_videos, team_performance, average_speed, getRankings, getTeamCCWM, getTeamDPRS, getTeamOPRS, getTeamRank, getTeamRecord, getPlayoffAlliances, determineDefense, getChargeConsistency, average_speed_topPercentile, max_speed, get_scoreBreakdown, match_predictWinner, getRealMatchScore, distanceFivePointMovingAverage, highestAverageVelocity, totalDistanceTraveled, fivePointAverageVelocity, get_matches, competition_match_data_all

year = 2023

formattedNames = []
namesList = get_events(year)
for name in namesList:
    formatted = f"{name[0]}, ({name[1]})"
    formattedNames.append(formatted)

formattedNames.remove("FIRST Long Island Regional #2, (2023nyli2)")
formattedNames.insert(0, "FIRST Long Island Regional #2, (2023nyli2)")
        
event = st.selectbox("Select an event", formattedNames)
event_key = event[event.index('('):]
event_key = event_key[1:-1]

# Get all the matches for the selected event and store them in a list
matches = competition_match_data_all(event_key)

# Store the match numbers in a list
match_numbers = []
match_teams = []
competition_levels = []
match_numericals = []
match_keys = []
for match in matches:
    match_numbers.append(match[0])
    match_teams.append(match[1])
    competition_levels.append(match[2])
    match_numericals.append(match[3])
    match_keys.append(match[4])

# Sort the match numbers and match teams by their competition level and match number
match_numbers, match_teams, competition_levels, match_numericals = zip(*sorted(zip(match_numbers, match_teams, competition_levels, match_numericals)))

# Create a box for the user to type in the match number they want to see data for. (Utilize typeahead)
match_number = st.selectbox("Select a match", match_numbers)

# Get the index of the match number the user selected
match_index = match_numbers.index(match_number)

match_key = match_keys[match_index]

# Get the match teams
match_teams = match_teams[match_index]

team1 = match_teams[0][3:]
team2 = match_teams[1][3:]
team3 = match_teams[2][3:]
team4 = match_teams[3][3:]
team5 = match_teams[4][3:]
team6 = match_teams[5][3:]

match_teams = [team1, team2, team3, team4, team5, team6]

# List and display the teams
st.markdown("**Teams in match " + str(match_number) + ":**")

# Display the teams in the match in a bullet list
#for team in match_teams:
    #st.markdown(f"- <span style=color:red>{team}</span>", unsafe_allow_html=True)

# Do the same thing as the code above, but display three teams per row
for i in range(0, len(match_teams), 3):
    st.markdown(f"- <span style=color:red>{match_teams[i]}</span> - <span style=color:red>{match_teams[i+1]}</span> - <span style=color:red>{match_teams[i+2]}</span>", unsafe_allow_html=True)

average_velocity_lists = []
error = 0

for team in match_teams:

    matches = competition_match_data(team, event_key)

    for match in matches:
        if match[5] == match_key:
            match = match

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

        average_velocities = fivePointAverageVelocity(xData, yData, times)
        average_velocity_lists.append((team, average_velocities))
                        
    except Exception as e:
        error += 1

# Create a line graph that uses each teams average_velocities list to plot the average velocity of each team over the course of the match
def plot_average_velocities(average_velocity_lists, team_numbers):
    
    data_frames = []

    # Match the team numbers that exist in the average_velocity_lists with the team numbers that exist in the team_numbers list. If a team number found in team_numbers is not in the average_velocity_lists, remove it from the team_numbers list
    for i in range(len(team_numbers) - 1):
        if team_numbers[i] not in [x[0] for x in average_velocity_lists]:
            team_numbers.remove(team_numbers[i])

    num_to_loop = len(team_numbers)
    for q in range(num_to_loop):
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

            # Loop through the teams and set team = to whichever team is equal to the team being looped through
            current_team = team_numbers[q]
            team_index = team_numbers.index(current_team)
            team_name = team_numbers[team_index]

            vel_list = average_velocity_lists[team_index][1]
            for j in range(len(vel_list)):
                if vel_list[j] <= bins[i]:
                    count += 1
            percentages.append((count/len(vel_list)) * 100)

        # Create a dataframe from the bins and percentages
        df = pd.DataFrame({'Velocity (ft/s)': bins, 'Cumulative Percent': percentages})

        # Convert the dataframe into data to make a line
        data = go.Scatter(x=df['Velocity (ft/s)'], y=df['Cumulative Percent'], mode='lines+markers', name='Team ' + str(team_name))

        # Store the line data in a list
        data_frames.append(data)

    # Plot the data
    fig = go.Figure(data=data_frames)

    # Set the y-axis to be between 0 and 100 with increments of 10
    fig.update_yaxes(range=[0, 100], dtick=10)

    # Set the x-axis to be between 2.5 and 17.5 with increments of .5
    fig.update_xaxes(range=[2.5, 17.5], dtick=.5)

    # The y-axis will be labeled "Cumulative Percent"
    # The x-axis will be labeled "Velocity (ft/s)"
    # The title will be "% of Measurements at or below Velocity X, but above 2 ft/s (For Match X)"

    # Set the title
    fig.update_layout(title="% of Measurements at or below Velocity X, but above 2 ft/s (For Match " + str(match_number) + ")")

    # Set the x-axis title
    fig.update_xaxes(title_text="Velocity (ft/s)")

    # Set the y-axis title
    fig.update_yaxes(title_text="Cumulative Percent")

    # Make the x-axis numbers right-side up
    fig.update_xaxes(tickangle=0)

    # Put more space between each number on the x-axis
    fig.update_xaxes(tickfont=dict(size=10))

    # plot the graph
    st.plotly_chart(fig)

plot_average_velocities(average_velocity_lists, match_teams)


# Add a warning mentioning that the data is generated using MotionWorks data
st.warning("All data shown is obtained from **Zebra MotionWorks** data through TheBlueAlliance API.", icon="⚠️")

# Add an info box to give credit
st.info("All data is provided by Longwood Robotics Team 564\n\nCreated by: Gregory Cohen, John Hirdt, Ryan Pfister\n\nFor questions and comments, please contact us at: john.hirdt@longwoodcsd.org\n\nTo visit our website, [click here](https://longwoodrobotics.com/)", icon="ℹ️")