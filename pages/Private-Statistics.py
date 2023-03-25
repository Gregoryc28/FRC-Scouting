# streamlit_app.py

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import requests
import traceback
from streamlit_player import st_player

# Data Visualization
from plotly.subplots import make_subplots
import plotly.graph_objects as go

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData, get_team_match_videos, team_performance, average_speed, getRankings, getTeamCCWM, getTeamDPRS, getTeamOPRS, getTeamRank, getTeamRecord, getPlayoffAlliances, determineDefense, getChargeConsistency, average_speed_topPercentile, max_speed

year = 2023
        
event = "FIRST Long Island Regional #1, (2023nyli)"
event_key = event[event.index('('):]
event_key = event_key[1:-1]
#event_key = "2023nyli1"

team_numbers = []

get_teams = get_events_teams(event_key)
for team in get_teams:
    team = team[team.index(','):]
    team = team[2:]

    while len(team) > 4:
        team = team[team.index(','):]
        team = team[2:]

    team_numbers.append(team)

def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True

if check_password():
    # We are going to create an algorithm that allows us to determine a leaderboard of the teams we would select if we are choosing our alliance.
    # One list will be for offensive robots, and one will be for defensive robots.

    offense_teams = []
    defense_teams = []
    times_in_defense_list = []

    # We will use our defense prediciton algorithm to determine which teams are good at defense and which are good at offense.

    for team in team_numbers:
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

                time_defense = determineDefense(team, event_key, match[2], times, xData, yData)
                times_in_defense_list.append(time_defense)

            except:
                pass

        # Get the average time the robot spends in a defense
        average_time_defense = round(sum(times_in_defense_list) / len(times_in_defense_list), 2)

        is_defense = False
        # Check if the average time the robot spends in a defense is greater than half the length of a match
        if average_time_defense > ((len(times)/10 - (len(times)/10 * .1)) / 3):
            is_defense = True

        if is_defense:
            defense_teams.append(team)
        else:
            offense_teams.append(team)

    # Now that we have which teams are offense and which are defense, we can do the following.
    # For defense: 
    #   we will internally without displaying the data, rank each defense team based on the following metrics. We will then add the rank of each team for each metric together and average them out.
    #       1. Rank by DPRs
    #       2. Rank by event rank

    # For offense:
    #   we will internally without displaying the data, rank each offense team based on the following metrics. We will then add the rank of each team for each metric together and average them out.
    #       1. Rank by OPRs
    #       2. Rank by average match score
    #       3. Rank by average cycles per match

    # First do the defensive ones.

    defense_teams_ranked_dprs = []
    defense_teams_ranked_event_rank = []
    defense_teams_final_rankings = []

    for team in defense_teams:
        defense_teams_ranked_dprs.append([team, getTeamDPRS(team, event_key)])
        defense_teams_ranked_event_rank.append([team, getTeamRank(team, event_key)])

    defense_teams_ranked_dprs.sort(key=lambda x: x[1])
    # Lower team rank is better 
    defense_teams_ranked_event_rank.sort(key=lambda x: x[1])

    for team in defense_teams:
        defense_teams_final_rankings.append([team, defense_teams_ranked_dprs.index([team, getTeamDPRS(team, event_key)]) + defense_teams_ranked_event_rank.index([team, getTeamRank(team, event_key)])])

    defense_teams_final_rankings.sort(key=lambda x: x[1])

    # Now do the offensive ones.

    offense_teams_ranked_oprs = []
    offense_teams_ranked_average_match_score = []
    offense_teams_ranked_average_cycles_per_match = []
    offense_teams_final_rankings = []

    for team in offense_teams:
        performance_stats = team_performance(team, event_key)
        avg_match_score = performance_stats[3]

        try:
            offense_teams_ranked_oprs.append([team, getTeamOPRS(team, event_key)])
        except:
            offense_teams_ranked_oprs.append([team, 0])
        try:
            offense_teams_ranked_average_match_score.append([team, avg_match_score])
        except:
            offense_teams_ranked_average_match_score.append([team, 0])

        matches = competition_match_data(team, event_key)
        # Sort the matches from earliest to latest
        matches.sort(key=lambda x: x[1])
        
        num_cycles_list = []
        
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

                except:
                    pass

            try:
                total_avg_cycles = round(sum(num_cycles_list) / len(num_cycles_list), 2)
            except:
                total_avg_cycles = 2

        except:
            total_avg_cycles = 2

        offense_teams_ranked_average_cycles_per_match.append([team, total_avg_cycles])

    offense_teams_ranked_oprs.sort(key=lambda x: x[1])
    # Lower team rank is better
    offense_teams_ranked_average_match_score.sort(key=lambda x: x[1])
    # More cycles is better
    offense_teams_ranked_average_cycles_per_match.sort(key=lambda x: x[1], reverse=True)

    for team in offense_teams:
        try:
            offense_teams_final_rankings.append([team, offense_teams_ranked_oprs.index([team, getTeamOPRS(team, event_key)]) + offense_teams_ranked_average_match_score.index([team, avg_match_score]) + offense_teams_ranked_average_cycles_per_match.index([team, total_avg_cycles])])
        except:
            pass

    offense_teams_final_rankings.sort(key=lambda x: x[1])

    # Now that we have the rankings, we can display them.

    st.write('Defense Teams:')
    for team in defense_teams_final_rankings:
        st.write(team[0])

    st.write('Offense Teams:')
    for team in offense_teams_final_rankings:
        st.write(team[0])

    

