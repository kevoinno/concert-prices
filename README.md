# concert-prices

## Project Overview

This project allows users to search a concert on TicketMaster and get data on ticket prices. The goal is to track the events ticket prices over time, so users can see when it is a good time to buy the tickets. The details about the event are stored in a database.


To do:

A. Build Historical Dataset First
Keep Airflow running locally for now
Add 5-10 popular events to track
Let it collect data for a week or two
This gives you real data to work with

B. Start Basic Webapp (in parallel)
Simple search functionality
Basic price history display
Use the data you're collecting

## Project Roadmap

### 1. Data Collection Setup (Started)
- Collect historical ticket prices daily
- Use existing tracking functionality in extract.py
- Set up automated scheduling with Airflow
- Let database collect price data for test events over time
- Build historical data needed for visualization
- Start with popular events for test dataset

### 2. Basic Webapp Structure
- Create simple webpage with:
  - Event search functionality 
  - Search results display
  - Price history view

### 3. Data Visualization
- Implement line graph showing:
  - Price on y-axis
  - Date on x-axis
- Use Chart.js or Plotly
- Focus on price over time visualization

### 4. User Interface
- Implement:
  - Search box
  - Event details display
  - Price history graph
  - Clean, basic styling

### 5. Integration
- Connect database to webapp
- Integrate Ticketmaster API search
- Display real-time and historical data
