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

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData, get_team_match_videos, team_performance, average_speed, getRankings, getTeamCCWM, getTeamDPRS, getTeamOPRS, getTeamRank, getTeamRecord, getPlayoffAlliances, determineDefense, getChargeConsistency, average_speed_topPercentile, max_speed, returnDefense, getRealMatchScore, match_predictWinner, get_scoreBreakdown, get_matches 

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
    matches = get_matches(event_key)

    st.title("Match Predictions Analysis")

    match_numbers = []
    matches = get_matches(event_key)
    # Sort the matches from earliest to latest
    for match in matches:
        match_numbers.append(match["match_number"])

    match_numbers.sort()

    working_matches = []
    for match in matches:
        if get_scoreBreakdown(match["key"]) != None:
            working_matches.append(match["key"])

    total_matches = len(working_matches)
    predicted_correctly = 0

    # Get the real match score to determine the winner of each match, and the predicted winner of each match
    for match in working_matches:
        real_data = getRealMatchScore(match)
        predicted_data = match_predictWinner(event_key, match)

        # Get the predicted winner of each match
        predicted_winner = predicted_data[0]
        
        # Get the real winner of each match
        if real_data[0] > real_data[1]:
            real_winner = "Red Alliance"
        elif real_data[0] < real_data[1]:
            real_winner = "Blue Alliance"

        # Check if the predicted winner is the same as the real winner
        if predicted_winner == real_winner:
            predicted_correctly += 1

    # Calculate the percentage of matches that were predicted correctly
    num_correct = predicted_correctly
    predicted_correctly = predicted_correctly / total_matches
    predicted_correctly = round(predicted_correctly * 100, 2)

    st.write("The predicted winner of each match was correct " + str(predicted_correctly) + "% of the time.")
    st.write("We predicted {} matches correctly out of {} matches.".format(num_correct, total_matches))