import streamlit as st
import requests
import os
import time

# --- Page Configuration ---
st.set_page_config(page_title="Apify Scraper Dev Tool", layout="wide")
st.title("Apify Scraper - JSON Inspector (V2)")
st.info("This app runs the specialized sportsbook scraper with the correct input from the official README.")

# --- API & ACTOR CONFIGURATION ---
APIFY_API_KEY = st.secrets.get("APIFY_API_KEY")
ACTOR_ID = "harvest/sportsbook-odds-scraper" 

# --- API Interaction Function ---
@st.cache_data(ttl=600)
def run_scraper_and_get_json(actor_id):
    """Triggers the sportsbook scraper with the correct input schema and returns the JSON result."""
    if not APIFY_API_KEY:
        return None, "Apify API key not found in Streamlit secrets."

    st.write("Starting sportsbook scraper with the correct input format...")
    
    # *** THIS IS THE FINAL FIX, BASED ON THE README YOU PROVIDED ***
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
    
    run_response = requests.post(
        f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_KEY}",
        json=actor_input
    )
    if run_response.status_code != 201:
        return None, f"Failed to start actor {actor_id}. Response: {run_response.text}"
    
    run_id = run_response.json()['data']['id']
    st.write(f"Scraper run started with ID: {run_id}. Waiting for completion (this may take a few minutes)...")

    while True:
        status_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}")
        status = status_response.json()['data']['status']
        if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT']:
            break
        time.sleep(10) # Wait a little longer between checks

    if status != 'SUCCEEDED':
        return None, f"Actor run {run_id} failed with status: {status}. Check the run log in your Apify account for details."

    st.success("Scraper finished successfully! Fetching results...")
    results_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_API_KEY}")
    
    return results_response.json(), None

# --- Main App Logic ---
st.header("Run the FanDuel Scraper")
st.write("This will trigger the scraper with the official input format and display the structured JSON data it returns.")

if st.button("Run Scraper"):
    
    raw_json_data, error = run_scraper_and_get_json(ACTOR_ID)

    if error:
        st.error(error)
    elif not raw_json_data:
        st.warning("Scraper ran but returned no data. Check the Actor run log in your Apify account.")
    else:
        st.success("Scraping complete! Raw JSON output is displayed below.")
        
        # Display the structured JSON result from the scraper
        st.json(raw_json_data)
        
        st.header("Next Step: Analyze the JSON")
        st.info("With this JSON, we can finally build the parser to display the data in a clean table.")

