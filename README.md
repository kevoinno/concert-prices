# concert-prices

## Project Overview

This project allows users to search a concert on TicketMaster and get data on ticket prices. The goal is to track the events ticket prices over time, so users can see when it is a good time to buy the tickets. The details about the event are stored in a database.


To do:
1. Need to use XCom to pass data from 1 task to another in Airflow
    - task 1 should push data to xcoms
    - task 2 should pull data from xcoms
2. Read chatgpt response to fix issue: Can't connect when running dag through airflow!

Notes:  
- The way Airflow was setup was using Docker
