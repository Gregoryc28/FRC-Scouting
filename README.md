# FIRST Robotics Scouting Application

An advanced analytics tool for FIRST Robotics Competition teams that leverages Zebra MotionWorks technology to track and analyze robot movements during matches.

## Overview

This application provides FIRST Robotics teams with powerful scouting capabilities by processing real-time tracking data to generate valuable insights about robot performance.

## Features

- **Robot Movement Analysis**: Track and visualize robot paths and movements during matches
- **Performance Metrics**: Calculate key statistics including speed, acceleration, and time spent in different zones
- **Match Predictions**: Generate match outcome predictions with 89% accuracy
- **Team Performance Stats**: Analyze win/loss records, cycle times, and scoring capabilities
- **Match Video Integration**: Access and review match videos directly within the application
- **Data Visualization**: Generate interactive charts and heatmaps of robot positions and movements

## Technology Stack

- **Backend**: Python with Streamlit for web application framework
- **API Integration**: TheBlueAlliance API for match data and Zebra MotionWorks for position tracking
- **Data Processing**: NumPy and Pandas for statistical analysis
- **Visualization**: Matplotlib and Plotly for interactive data visualization
- **Video Integration**: YouTube embedded players for match review

## How It Works

The application connects to TheBlueAlliance API to fetch match and team data, then processes Zebra MotionWorks tracking data to analyze robot movements. This data is used to calculate performance metrics, generate visualizations, and predict match outcomes.

## Usage

1. Select an event from the dropdown menu
2. Choose a team to analyze
3. Select the type of data you want to view:
   - Team Performance Stats
   - Match Videos
   - Event Stats
   - Match Predictions
   - Cycle Data
   - Robot Stats
   - Charge Data
   - Motion Stats

## Project Contributors

- Gregory Cohen (Lead Developer)
- John Hirdt
- Ryan Pfister

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Longwood Robotics Team 564
- FIRST Robotics Competition
- TheBlueAlliance for their comprehensive API
- Zebra MotionWorks for their tracking technology
