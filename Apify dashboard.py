import streamlit as st
import requests
import os

# --- Page Configuration ---
st.set_page_config(page_title="API Debugger", layout="wide")
st.title("API Debugger for Apify")
st.error("This app's only purpose is to make one API call and show the raw server response.")

# --- API & ACTOR CONFIGURATION ---
APIFY_API_KEY = st.secrets.get("APIFY_API_KEY")
ACTOR_ID = "harvest/sportsbook-odds-scraper" 

# --- Main App Logic ---
st.header("Run a Single API Request")

if st.button("Make API Call"):

    if not APIFY_API_KEY:
        st.error("FAILURE: The secret 'APIFY_API_KEY' was not found. The app cannot proceed.")
    else:
        st.success("API Key was found successfully! Proceeding to make the API call.")

        # This is the exact input from the official README
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
        
        st.subheader("Sending this JSON input to the server:")
        st.json(actor_input)

        st.subheader("Server Response:")
        
        try:
            # Make the single POST request to start the Actor run
            run_response = requests.post(
                f"https://api.apify.com/v2/acts/{actor_id}/runs?token={APIFY_API_KEY}",
                json=actor_input
            )

            # --- THIS IS THE ENTIRE GOAL ---
            # We will print everything about the response we get back

            st.write(f"**Status Code:** `{run_response.status_code}`")
            
            st.write("**Raw Response Text:**")
            st.code(run_response.text, language="text")

            # Try to show it as JSON if possible, but don't crash if it's not
            try:
                st.write("**Response as JSON (if valid):**")
                st.json(run_response.json())
            except requests.exceptions.JSONDecodeError:
                st.error("The server response was not valid JSON.")

        except Exception as e:
            st.error(f"A critical error occurred during the request itself: {e}")

