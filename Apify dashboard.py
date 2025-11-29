import streamlit as st
import requests
import os
import time

# --- Page Configuration ---
st.set_page_config(page_title="Apify Scraper Dev Tool", layout="wide")
st.title("Apify Scraper - JSON Inspector (V2)")
st.info("This app runs the sportsbook 'Task' with the correct API endpoint.")

# --- API & ACTOR CONFIGURATION ---
APIFY_API_KEY = st.secrets.get("APIFY_API_KEY")
# This is an ACTOR TASK ID, not just an Actor ID
ACTOR_TASK_ID = "harvest/sportsbook-odds-scraper" 

# --- API Interaction Function ---
@st.cache_data(ttl=600)
def run_task_and_get_json(task_id):
    """Triggers an Apify Actor TASK and returns the direct JSON result."""
    if not APIFY_API_KEY:
        return None, "Apify API key not found in Streamlit secrets."

    st.write("Starting sportsbook task with the correct endpoint...")
    
    actor_input = {
        "sport": "americanfootball_nfl",
        "bookmakers": ["fanduel"],
        "markets": ["h2h", "spreads", "totals"],
        "regions": ["us"],
        "proxyConfiguration": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
    
    # *** THIS IS THE FINAL FIX ***
    # The URL must use "/actor-tasks/", not "/acts/".
    start_url = f"https://api.apify.com/v2/actor-tasks/{task_id}/runs?token={APIFY_API_KEY}"
    
    run_response = requests.post(start_url, json=actor_input)

    if run_response.status_code != 201:
        return None, f"Failed to start task. Status: {run_response.status_code}. Response: {run_response.text}"
    
    run_id = run_response.json()['data']['id']
    st.write(f"Task run started with ID: {run_id}. Waiting for completion...")

    while True:
        status_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}")
        status = status_response.json()['data']['status']
        if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT']:
            break
        time.sleep(10)

    if status != 'SUCCEEDED':
        return None, f"Task run {run_id} failed with status: {status}. Check the run log in your Apify account for details."

    st.success("Task finished successfully! Fetching results...")
    results_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_API_KEY}")
    
    return results_response.json(), None

# --- Main App Logic ---
st.header("Run the FanDuel Scraper Task")
st.write("This will trigger the scraper and display the structured JSON data it returns.")

if st.button("Run Scraper Task"):
    
    raw_json_data, error = run_task_and_get_json(ACTOR_TASK_ID)

    if error:
        st.error(error)
    elif not raw_json_data:
        st.warning("Task ran but returned no data. Check the Actor run log in your Apify account.")
    else:
        st.success("Scraping complete! Raw JSON output is displayed below.")
        st.json(raw_json_data)
        st.header("Next Step: Analyze the JSON")
        st.info("With this JSON, we can finally build the parser to display the data in a clean table.")
