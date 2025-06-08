# police_log
📘 Theoretical Explanation – Police Traffic Stop Log Analysis using Streamlit & SQL
🧠 Project Title:
"Check Post Traffic Stop Analysis and Prediction using Streamlit and SQL"

🎯 Objective:
The objective of this project is to analyze police traffic stop data, uncover trends in violations, demographic patterns, and high-risk behavior, and create a Streamlit dashboard for interactive visualization and insights. This aids law enforcement in making data-driven decisions and quicker operations at checkpoints.

🗃️ Dataset Description:
Multiple CSV files were used:

cleaned_traffic_stops.csv

final_traffic_stops.csv

formatted_traffic_stops.csv

traffic_stops_with_vehicle_number.csv

Each file includes columns like:

stop_date, stop_time

driver_gender, driver_age, driver_race

violation, search_conducted, is_arrested

country_name, vehicle_number

stop_duration, is_drug_related, etc.

🔨 Tools and Technologies Used:
Tool	Purpose
Python	Data processing and logic
Pandas	Data manipulation
Streamlit	Web dashboard interface
SQL (PostgreSQL)	Querying data
GitHub	Version control and hosting
VS Code	IDE for coding

🧮 Key Features Implemented:
✅ 1. Data Cleaning & Formatting:
Null value handling

Type conversion (date/time parsing)

Exporting formatted data into new CSVs

Dataset combined and normalized

📊 2. Streamlit Dashboard Modules:
Summary Metrics (Total Stops, Arrests, Searches)

Vehicle Logs filterable by:

Country

Violation

Vehicle Number

Officer Logs section

Top 10 Violations (Bar chart)

High-Risk Vehicles section (SQL-driven)

🧠 3. Advanced SQL Insights:
All listed below were implemented via dynamic queries:

Top 10 Vehicles in Drug-Related Stops

Most Frequently Searched Vehicles

Driver Age Group with Highest Arrest Rate

Gender Distribution per Country

Most Common Violation by Age (<25)

Stop Duration vs. Arrest Likelihood (Time Analysis)

Arrest Rate by Violation and Country

Year-Month-Hour Based Stop Count

Violation Categories with Low Arrests/Searches

📈 Results / Outcomes:
Faster insights into traffic behavior

Efficient check post monitoring

Predictive filtering based on age/race/time

Real-time report generation for field use

🔐 Challenges Faced:
SQL errors due to missing fields (e.g., drug_related)

Data parsing issues (stop_time as None)

Integration bugs with Streamlit inputs and outputs

Version control conflicts (solved using Git)

✅ Project Deliverables:
✅ Python Scripts (Data handling and Streamlit)

✅ SQL Query Set (for dynamic insights)

✅ Streamlit Dashboard App

✅ CSV Files (Cleaned and final)

✅ GitHub Repo (Version controlled)

✅ README.md + Theoretical Documentation

📚 Future Enhancements:
Add role-based login for officers

Use ML model for predicting violations

Export reports as PDFs

Add map view for country-wise incidents

