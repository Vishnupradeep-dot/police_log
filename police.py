import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from decimal import Decimal

# ✅ This must be the first Streamlit command
st.set_page_config(page_title="SecureCheck - ThemeLights", layout="wide")

# ------------------------------
# DB CONNECTION
# ------------------------------
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        dbname="traffic_data",
        user="postgres",
        password="9791804453",   
        host="localhost",
        port="5432"
    )

conn = get_connection()
cur = conn.cursor()

# ------------------------------
# SQL QUERY RUNNER
# ------------------------------
def run_query(query):
    try:
        cur.execute(query)
        results = cur.fetchall()
        df = pd.DataFrame(results, columns=[desc[0] for desc in cur.description])
        df = df.map(lambda x: int(x) if isinstance(x, Decimal) else x)
        return df
    except Exception as e:
        st.error(f"\u274c SQL Error: {e}")
        conn.rollback()
        return pd.DataFrame()

# ------------------------------
# DASHBOARD TITLE
# ------------------------------
st.title("\U0001F698 SecureCheck Dashboard")
st.markdown("---")

# ------------------------------
# 1: KPI METRICS
# ------------------------------
st.subheader("\U0001F4C8 Summary Metrics")

kpi_total = "SELECT COUNT(*) FROM traffic_stops;"
kpi_search = "SELECT COUNT(*) FROM traffic_stops WHERE search_conducted = TRUE;"
kpi_arrest = "SELECT COUNT(*) FROM traffic_stops WHERE is_arrested = TRUE;"

col1, col2, col3 = st.columns(3)
col1.metric("Total Stops", run_query(kpi_total).iloc[0, 0])
col2.metric("Search Count", run_query(kpi_search).iloc[0, 0])
col3.metric("Arrest Count", run_query(kpi_arrest).iloc[0, 0])

# ------------------------------
# 2: VEHICLE LOGS
# ------------------------------
st.subheader("\U0001F698 Vehicle Logs, Violations, Officer Reports")

filter_country = st.sidebar.text_input("Country (optional)")
filter_violation = st.sidebar.text_input("Violation (optional)")
filter_vehicle = st.sidebar.text_input("Vehicle Number (optional)")

log_query = '''
SELECT stop_date, stop_time, country_name, driver_gender, driver_age,
       driver_race, violation, search_conducted, is_arrested,
       vehicle_number
FROM traffic_stops
'''

conditions = []
if filter_country:
    conditions.append(f"country_name = '{filter_country}'")
if filter_violation:
    conditions.append(f"violation = '{filter_violation}'")
if filter_vehicle:
    conditions.append(f"vehicle_number = '{filter_vehicle}'")
if conditions:
    log_query += " WHERE " + " AND ".join(conditions)
log_query += " ORDER BY stop_date DESC LIMIT 100;"

vehicle_logs_df = run_query(log_query)
st.dataframe(vehicle_logs_df, use_container_width=True)

##--New Police Log & Predict Outcome and Violation
##-----------------
st.subheader("🚨 Add New Police Log & Predict Outcome and Violation")

# Form inputs
with st.form("new_log_form"):
    stop_date = st.date_input("Stop Date")
    stop_time = st.time_input("Stop Time")
    country = st.text_input("Country Name")

    driver_gender = st.selectbox("Driver Gender", ["male", "female", "other"])
    driver_age = st.number_input("Driver Age", min_value=16, max_value=100)
    driver_race = st.text_input("Driver Race")

    is_search = st.selectbox("Was a Search Conducted?", [0, 1])
    search_type = st.text_input("Search Type")

    is_drug_related = st.selectbox("Was it Drug Related?", [0, 1])

    stop_duration = st.selectbox("Stop Duration", ["0-15 Min", "16-30 Min", "30+ Min"])
    vehicle_number = st.text_input("Vehicle Number")

    submitted = st.form_submit_button("Predict Stop Outcome & Violation")

# Dummy logic to display a prediction (replace this with ML logic or SQL-based rules)
if submitted:
    st.success("✅ Log received and processed!")

    # Example response output
    predicted_outcome = "Citation"
    predicted_violation = "Speeding"

    st.markdown(f"""
        ### 🔍 Prediction Result:
        - **Outcome**: `{predicted_outcome}`
        - **Likely Violation**: `{predicted_violation}`
    """)


#-------------------------------------------------------

# Dictionary of advanced SQL queries
queries = {
# SQL Query: 
 "Top 10 vehicles in drug-related stops":'''
SELECT vehicle_number, COUNT(*) AS stop_count
FROM traffic_stops
WHERE drugs_related_stop = TRUE
GROUP BY vehicle_number
ORDER BY stop_count DESC
LIMIT 10;
''',
"Which Vehicles Were Most Frequently Searched":'''
SELECT vehicle_number, COUNT(*) AS search_count
FROM traffic_stops
WHERE search_conducted = TRUE
GROUP BY vehicle_number
ORDER BY search_count DESC
LIMIT 10;
''',
"Which Driver Age Group Had the Highest Arrest Rate": '''
SELECT driver_age, COUNT(*) AS arrest_count
FROM traffic_stops
WHERE is_arrested = TRUE
GROUP BY driver_age
ORDER BY arrest_count DESC
LIMIT 10;
''',
"Gender Distribution of Drivers Stopped in Each Country" : '''
SELECT country_name, driver_gender, COUNT(*) AS count
FROM traffic_stops
GROUP BY country_name, driver_gender
ORDER BY country_name, count DESC;
''',
"Which Race and Gender Combination Has the Highest Search Rate": '''
SELECT driver_race, driver_gender, COUNT(*) AS search_count
FROM traffic_stops
WHERE search_conducted = TRUE
GROUP BY driver_race, driver_gender
ORDER BY search_count DESC
LIMIT 10;
''',
"What Time of Day Sees the Most Traffic Stops" : '''
SELECT EXTRACT(HOUR FROM stop_time::time) AS hour_of_day, COUNT(*) AS stop_count
FROM traffic_stops
GROUP BY hour_of_day
ORDER BY stop_count DESC
LIMIT 10;
''',
"Average Stop Duration for Different Violations":'''
SELECT violation, AVG(
    CASE 
        WHEN stop_duration = '<5 min' THEN 5
        WHEN stop_duration = '6-15 min' THEN 10
        WHEN stop_duration = '16-30 min' THEN 23
        ELSE 45
    END
) AS avg_duration
FROM traffic_stops
GROUP BY violation
ORDER BY avg_duration DESC;
''',
"Are Night Stops More Likely to Lead to Arrests":'''
SELECT 
    CASE 
        WHEN EXTRACT(HOUR FROM stop_time::time) BETWEEN 0 AND 5 THEN 'Night'
        ELSE 'Day'
    END AS time_of_day,
    COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
FROM traffic_stops
GROUP BY time_of_day;
''',
"Violations Most Associated with Searches or Arrests": '''
SELECT violation, 
       COUNT(CASE WHEN search_conducted = TRUE THEN 1 END) AS search_count,
       COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) AS arrest_count
FROM traffic_stops
GROUP BY violation
ORDER BY search_count DESC, arrest_count DESC
LIMIT 10;
''',
"Violations Most Common Among Younger Drivers (<25)":'''
SELECT violation, COUNT(*) AS count
FROM traffic_stops
WHERE driver_age < 25
GROUP BY violation
ORDER BY count DESC
LIMIT 10;
''',
"Violations Rarely Leading to Search or Arrest": '''
SELECT 
    violation,
    COUNT(*) AS total_stops,
    COUNT(CASE WHEN search_conducted = TRUE THEN 1 END) AS search_count,
    COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) AS arrest_count
FROM traffic_stops
GROUP BY violation
ORDER BY total_stops DESC;
''',
"Countries Reporting Highest Rate of Drug-Related Stops": '''
SELECT country_name, COUNT(*) AS drug_stop_count
FROM traffic_stops
WHERE drugs_related_stop = TRUE
GROUP BY country_name
ORDER BY drug_stop_count DESC
LIMIT 10;
''',
"Arrest Rate by Country and Violation": '''
SELECT country_name, violation,
       COUNT(*) AS total_stops,
       COUNT(CASE WHEN is_arrested = TRUE THEN 1 END) * 100.0 / COUNT(*) AS arrest_rate
FROM traffic_stops
GROUP BY country_name, violation
ORDER BY arrest_rate DESC
LIMIT 10;
''',
"Countries with Most Stops Where Search Was Conducted": '''
SELECT country_name, COUNT(*) AS search_count
FROM traffic_stops
WHERE search_conducted = TRUE
GROUP BY country_name
ORDER BY search_count DESC
LIMIT 10;
''',
"Driver Violation Trends Based on Age and Race":'''
SELECT driver_age, driver_race, violation, COUNT(*) AS count
FROM traffic_stops
GROUP BY driver_age, driver_race, violation
ORDER BY count DESC
LIMIT 10;
''',
"Number of Stops by Year, Month, Hour":'''
SELECT 
    EXTRACT(YEAR FROM stop_date) AS year,
    EXTRACT(MONTH FROM stop_date) AS month,
    EXTRACT(HOUR FROM stop_time::time) AS hour,
    COUNT(*) AS stop_count
FROM traffic_stops
WHERE stop_date IS NOT NULL
GROUP BY year, month, hour
ORDER BY year, month, hour;
''',
"Number of Stops by Year, Month, Hour":'''
SELECT 
    EXTRACT(YEAR FROM stop_date) AS year,
    EXTRACT(MONTH FROM stop_date) AS month,
    EXTRACT(HOUR FROM stop_time::time) AS hour,
    COUNT(*) AS stop_count
FROM traffic_stops
WHERE stop_date IS NOT NULL
GROUP BY year, month, hour
ORDER BY year, month, hour;
''',
"Violations with High Search and Arrest Rates ":'''
SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS search_count,
    ROUND(SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END)::decimal * 100 / COUNT(*), 2) AS search_rate,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrest_count,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::decimal * 100 / COUNT(*), 2) AS arrest_rate,
    RANK() OVER (ORDER BY SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END)::decimal / COUNT(*) DESC) AS search_rank,
    RANK() OVER (ORDER BY SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::decimal / COUNT(*) DESC) AS arrest_rank
FROM traffic_stops
GROUP BY violation
ORDER BY search_rate DESC, arrest_rate DESC;
''',
"Driver Demographics by Country (Age, Gender, and Race)":'''
SELECT 
    country_name,
    driver_age,
    driver_gender,
    driver_race,
    COUNT(*) AS stop_count
FROM traffic_stops
GROUP BY country_name, driver_age, driver_gender, driver_race
ORDER BY country_name, stop_count DESC;
''',
"Top 5 Violations with Highest Arrest Rates": '''
SELECT 
    violation,
    COUNT(*) AS total_stops,
    SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS total_arrests,
    ROUND(SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END)::decimal * 100 / COUNT(*), 2) AS arrest_rate
FROM traffic_stops
WHERE is_arrested IS NOT NULL
GROUP BY violation
ORDER BY arrest_rate DESC
LIMIT 5;
'''
}

st.title("Advanced Police Traffic Stop Insights")
selected_query = st.selectbox("Select a Query to Run", list(queries.keys()))

if selected_query:
    query = queries[selected_query]
    cur.execute(query)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    df = pd.DataFrame(rows, columns=columns)
    st.dataframe(df)


# ------------------------------
# 3: TOP VIOLATIONS CHART
# ------------------------------
st.subheader("\U0001F4CA Top 10 Violations")

top_violations_query = '''
SELECT violation, COUNT(*) AS stop_count
FROM traffic_stops
GROUP BY violation
ORDER BY stop_count DESC
LIMIT 10;
'''
top_violations_df = run_query(top_violations_query)
if not top_violations_df.empty:
    fig1 = px.bar(top_violations_df, x='violation', y='stop_count', color='violation', title="Top Violations")
    st.plotly_chart(fig1, use_container_width=True)

# ------------------------------
# 4: HIGH-RISK VEHICLES
# ------------------------------
st.subheader("\U0001F6A8 High-Risk Vehicles")

risk_query = '''
SELECT vehicle_number,
       COUNT(*) AS total_stops,
       SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) AS searches,
       SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) AS arrests
FROM traffic_stops
GROUP BY vehicle_number
HAVING SUM(CASE WHEN search_conducted = TRUE THEN 1 ELSE 0 END) > 2
    OR SUM(CASE WHEN is_arrested = TRUE THEN 1 ELSE 0 END) > 1
ORDER BY arrests DESC, searches DESC
LIMIT 20;
'''
df_risk = run_query(risk_query)
st.dataframe(df_risk, use_container_width=True)

##--Example Summary
if not vehicle_logs_df.empty:
    row = vehicle_logs_df.iloc[0]
    if pd.notnull(row['stop_time']):
        time = pd.to_datetime(row['stop_time'], errors='coerce').strftime('%I:%M %p')
    else:
        time = "an unknown time"

if not vehicle_logs_df.empty:
    row = vehicle_logs_df.iloc[0]

    driver_age = int(row['driver_age']) if pd.notnull(row['driver_age']) else "unknown"
    driver_gender = "male" if row['driver_gender'] == 'M' else "female"
    violation = row['violation'] if pd.notnull(row['violation']) else "unknown violation"

    # Time handling
    if pd.notnull(row['stop_time']):
        try:
            time = pd.to_datetime(row['stop_time'], errors='coerce').strftime('%I:%M %p')
        except Exception:
            time = "an unknown time"
    else:
        time = "an unknown time"

    # Text details
    search_text = "No search was conducted" if not row['search_conducted'] else "A search was conducted"
    arrest_text = "he received a citation" if not row['is_arrested'] else "he was arrested"
    duration_text = "The stop lasted 6–15 minutes"
    drug_text = "and was not drug-related"

    summary = f"🚗 A {driver_age}-year-old {driver_gender} driver was stopped for **{violation}** at {time}. {search_text}, and {arrest_text}. {duration_text} {drug_text}."

    st.markdown("### 🧾 Example Summary")
    st.success(summary)






