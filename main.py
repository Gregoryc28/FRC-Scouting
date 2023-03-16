import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math
import requests

from data import competition_match_data, zebra_data_pull, zebra_data_quarterfinals_pull, zebra_data_semifinals_pull, zebra_data_finals_pull, zebra_speed, get_zoneData, get_events, get_events_teams, zebra_speed_percentile_graph, zebra_zone_percentile_piegraph, get_autoChargeConfirmation, get_timeChargingAuto, get_cycleData

#team = 564
teams = [564, 870, 263, 514, 527, 694]

# Create a streamlit select box for the user to select the team they want to see
#team = st.selectbox("Select a team", teams)

team = teams[0]
year = 2023

formattedNames = []
namesList = get_events(year)
for name in namesList:
    formatted = f"{name[0]}, ({name[1]})"
    formattedNames.append(formatted)
        
event = st.selectbox("Select an event", formattedNames)
event_key = event[event.index('('):]
event_key = event_key[1:-1]

team_numbers = []

get_teams = get_events_teams(event_key)
for team in get_teams:
    team = team[team.index(','):]
    team = team[2:]
    team_numbers.append(team)

teams = st.selectbox("Select a team", team_numbers)
team = teams
#team = teams[teams.index(','):]
#team = team[2:]

data_selection_choices = ["Cycle-Data", "Charge-Data", "Robot-Stats", "Team-Performance-Stats"]

data_selector = st.selectbox("Select a type of Data to search for", data_selection_choices)



''' Old code tested with new event/team inputs '''

matches = competition_match_data(team, event_key)
# Sort the matches from earliest to latest
matches.sort(key=lambda x: x[1])

time_charging_auto = []
charging_confirms_auto = []
num_cycles_list = []
avg_time_cross_list = []

num_cycles_leaderboard = []
avg_time_cycle_leaderboard = []
working_teams = []

gather_teams = get_events_teams(event_key)

for team in gather_teams:
    try:
        team = team[team.index(','):]
        team = team[2:]
        matches = competition_match_data(team, event_key)
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
            #times, xData, yData = zebra_data_pull(match[0], match[1], match[2], match[3])
            #zoneData = get_zoneData(team, event, match, times, xData, yData)
            #pie_graph = zebra_zone_percentile_piegraph(zoneData, team, match[1], match[2], match_type)
            #if pie_graph != 7:
                #st.pyplot(pie_graph)
            match_key = str(match[5])
            cycle_data = get_cycleData(match_key, match[2], times, xData)
            num_cycles_list.append(cycle_data[1])
            if cycle_data[0] != 7777:
                avg_time_cross_list.append(cycle_data[0])
            else:
                pass
            #time_to_charge_auto = get_timeChargingAuto(team, event, match, times, xData, yData)
            #time_charging_auto.append(time_to_charge_auto)
            #confirm_auto = get_autoChargeConfirmation(match_key, match[2], match[3])
            #charging_confirms_auto.append(confirm_auto)
            #st.write(get_autoChargeConfirmation(match_key, match[2], match[3]))
        
        total_avg_cycles = sum(num_cycles_list) / len(num_cycles_list)
        total_avg_time_cycle = sum(avg_time_cross_list) / len(avg_time_cross_list)
        
        num_cycles_leaderboard.append(total_avg_cycles)
        avg_time_cycle_leaderboard.append(total_avg_time_cycle)
        
        working_teams.append(team)
    except:
        pass

#st.write(f"Team {team} completes an average of {total_avg_cycles} cycles per match.")
#st.write(f"The average time it takes the team to complete a cycle is: \n{total_avg_time_cycle}")

final_leaderboard = []
current_pos = 0

for team in working_teams:
    final_leaderboard.append((team, num_cycles_leaderboard[current_pos], avg_time_cycle_leaderboard[current_pos]))
    
    current_pos += 1

# Sort the list of tuples based on the second element (average number of cycles)
sorted_teams = sorted(final_leaderboard, key=lambda x: x[1], reverse=True)

# Display the sorted list in a table format using Streamlit
st.write('## Leaderboard')
table_header = ['Team', 'Average Cycles', 'Average Time per Cycle']
table_rows = [[team[0], team[1], team[2]] for team in sorted_teams]
st.table([table_header] + table_rows)
    
#st.write(final_leaderboard)


'''avg_time_charging_auto = sum(time_charging_auto) / len(time_charging_auto)
st.write(f"The average time spent on the charge station during autonomous of each match for team {team}, was: \n{avg_time_charging_auto}")

num_successful_charges_auto = 0
num_docked_auto = 0
num_engaged_auto = 0
for item in charging_confirms_auto:
    if item in ("Docked", "Engaged"):
        num_successful_charges_auto += 1
        if item == "Docked":
            num_docked_auto += 1
        else:
            num_engaged_auto += 1
    else:
        pass

st.write(f"The number of successful times this team gained points from charging during autonomous was: \n{num_successful_charges_auto}")
st.write(f"The number of times the team successfully DOCKED during autonomous was: \n{num_docked_auto}")
st.write(f"The number of times the team successfully ENGAGED during autonomous was: \n{num_engaged_auto}")

num_attempted_charges_auto = 0
for item in time_charging_auto:
    if item != 0:
        num_attempted_charges_auto += 1
    else:
        pass

if num_successful_charges_auto != 0:
    success_percent_auto = (num_attempted_charges_auto / num_successful_charges_auto) * 100
else:
    success_percent_auto = 0

st.write(f"The success rate of this team charging in auto was: \n{success_percent_auto}")


st.write(time_charging_auto)'''