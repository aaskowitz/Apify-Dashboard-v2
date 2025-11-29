import streamlit as st
import requests
import os
import time

# --- Page Configuration ---
st.set_page_config(page_title="Apify Scraper Dev Tool", layout="wide")
st.title("Apify Scraper - JSON Inspector (V2)")
st.info("This app runs the sportsbook scraper with the corrected parsing logic.")

# --- API & ACTOR CONFIGURATION ---
APIFY_API_KEY = st.secrets.get("APIFY_API_KEY")
ACTOR_ID = "harvest/sportsbook-odds-scraper" 

# --- API Interaction Function ---
@st.cache_data(ttl=600)
def run_scraper_and_get_json(actor_id):
    if not APIFY_API_KEY:
        return None, "Apify API key not found in Streamlit secrets."

    st.write("Starting sportsbook scraper with the correct input format...")
    
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
        return None, f"Failed to start actor. Status: {run_response.status_code}. Response: {run_response.text}"
    
    # --- THIS IS THE FIX ---
    # The API returns a LIST with one item. We must access the first item with [0].
    response_data = run_response.json()
    run_id = response_data[0]['data']['id']
    
    st.write(f"Scraper run started with ID: {run_id}. Waiting for completion...")

    while True:
        status_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}?token={APIFY_API_KEY}")
        status_data = status_response.json()
        # The status response is NOT a list, so we access it directly.
        status = status_data['data']['status']
        if status in ['SUCCEEDED', 'FAILED', 'TIMED_OUT']:
            break
        time.sleep(10)

    if status != 'SUCCEEDED':
        return None, f"Actor run {run_id} failed with status: {status}. Check the run log in your Apify account."

    st.success("Scraper finished successfully! Fetching results...")
    results_response = requests.get(f"https://api.apify.com/v2/actor-runs/{run_id}/dataset/items?token={APIFY_API_KEY}")
    
    return results_response.json(), None

# --- Main App Logic ---
st.header("Run the FanDuel Scraper")
st.write("This will trigger the scraper and display the structured JSON data it returns.")

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

