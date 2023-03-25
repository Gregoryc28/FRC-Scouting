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
import pandas as pd

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData, get_team_match_videos, team_performance, average_speed, getRankings, getTeamCCWM, getTeamDPRS, getTeamOPRS, getTeamRank, getTeamRecord, getPlayoffAlliances, determineDefense, getChargeConsistency, average_speed_topPercentile, max_speed, returnDefense

year = 2023
        
event = "FIRST Long Island Regional #2, (2023nyli2)"
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
    # # We are going to create an algorithm that allows us to determine a leaderboard of the teams we would select if we are choosing our alliance.
    # # One list will be for offensive robots, and one will be for defensive robots.

    offense_teams = []
    defense_teams = []

    # # We will use our defense prediciton algorithm to determine which teams are good at defense and which are good at offense.

    for team in team_numbers:
        
        defense_teams.append(team)
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

    # Higher DPRs is better
    defense_teams_ranked_dprs.sort(key=lambda x: x[1], reverse=True)

    # # Now do the offensive ones.

    offense_teams_ranked_oprs = []
    # offense_teams_ranked_average_match_score = []
    # offense_teams_ranked_average_cycles_per_match = []
    # cycles_list = []
    # offense_teams_final_rankings = []

    for team in offense_teams:
        team_oprs = getTeamOPRS(team, event_key)
        offense_teams_ranked_oprs.append([team, team_oprs])

    st.write("LISTS")

    # Display pandas dataframes for the rankings (One for offense and one for defense)
    offense_teams_ranked_oprs_df = pd.DataFrame(offense_teams_ranked_oprs, columns=['Team', 'OPRs'])
    offense_teams_ranked_oprs_df = offense_teams_ranked_oprs_df.set_index('Team')
    offense_teams_ranked_oprs_df = offense_teams_ranked_oprs_df.sort_values(by=['OPRs'], ascending=False)
    st.table(offense_teams_ranked_oprs_df)

    defense_teams_ranked_dprs_df = pd.DataFrame(defense_teams_ranked_dprs, columns=['Team', 'DPRs'])
    defense_teams_ranked_dprs_df = defense_teams_ranked_dprs_df.set_index('Team')
    defense_teams_ranked_dprs_df = defense_teams_ranked_dprs_df.sort_values(by=['DPRs'], ascending=False)
    st.table(defense_teams_ranked_dprs_df)

    #     matches = competition_match_data(team, event_key)
    #     # Sort the matches from earliest to latest
    #     matches.sort(key=lambda x: x[1])
        
    #     num_cycles_list = []
        
    #     try:
    #         for match in matches:
    #             try:
    #                 # Check if the match is a qualification match (qm), quarterfinal (qf), semifinal (sf), or final (f)
    #                 if match[4] == 'qm':
    #                     match_type = 'Qualification'
    #                     times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
    #                 elif 'qf' in match[4]:
    #                     match_type = 'Quarterfinal'
    #                     times, xData, yData = zebra_data_quarterfinals_pull(match[0], match[1], match[2], match[3], match[4])
    #                 elif 'sf' in match[4]:
    #                     match_type = 'Semifinal'
    #                     times, xData, yData = zebra_data_semifinals_pull(match[0], match[1], match[2], match[3], match[4])
    #                 elif 'f' in match[4] and 'qf' not in match[4] and 'sf' not in match[4]:
    #                     match_type = 'Final'
    #                     times, xData, yData = zebra_data_finals_pull(match[0], match[1], match[2], match[3], match[4])
        
    #                 match_key = str(match[5])
    #                 cycle_data = get_cycleData(match_key, match[2], times, xData, yData)
    #                 num_cycles_list.append(cycle_data[1])

    #             except:
    #                 pass

    #         try:
    #             total_avg_cycles = round(sum(num_cycles_list) / len(num_cycles_list), 2)
    #         except:
    #             total_avg_cycles = 2

    #     except:
    #         total_avg_cycles = 2

    #     offense_teams_ranked_average_cycles_per_match.append([team, total_avg_cycles])
    #     cycles_list.append(total_avg_cycles)

    # # Higher OPRs is better
    # offense_teams_ranked_oprs.sort(key=lambda x: x[1], reverse=True)
    # # Lower team rank is better
    # offense_teams_ranked_average_match_score.sort(key=lambda x: x[1])
    # # More cycles is better
    # offense_teams_ranked_average_cycles_per_match.sort(key=lambda x: x[1], reverse=True)
    # # sort the cycles list from highest to lowest
    # cycles_list.sort(reverse=True)

    # countCycles = 0
    # for team in offense_teams:
    #     team_oprs = getTeamOPRS(team, event_key)
    #     performance_stats = team_performance(team, event_key)
    #     avg_match_score = performance_stats[3]
    #     average_cycles = cycles_list[countCycles]
    #     try:
    #         offense_teams_final_rankings.append([team, offense_teams_ranked_oprs.index([team, team_oprs]) + offense_teams_ranked_average_match_score.index([team, avg_match_score]) + cycles_list.index(average_cycles)])
    #         countCycles += 1
    #     except:
    #         pass

    # offense_teams_final_rankings.sort(key=lambda x: x[1])

    # # Now that we have the rankings, we can display them.

    # st.write('Defense Teams:')
    # # Display the rankings nicely
    # defense_teams_final_rankings_df = pd.DataFrame(defense_teams_final_rankings, columns=['Team', 'Rank'])
    # st.table(defense_teams_final_rankings_df)
    # # Highlight the teams in green and then slowly gradient lighter and lighter


    # st.write('Offense Teams:')
    # offense_teams_final_rankings_df = pd.DataFrame(offense_teams_final_rankings, columns=['Team', 'Rank'])
    # st.table(offense_teams_final_rankings_df)
