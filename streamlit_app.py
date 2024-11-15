import streamlit as st
import requests
from datetime import datetime, timedelta

# Set the page configuration
st.set_page_config(
    page_title="Simplified NewsAPI Explorer",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("📰 Simplified NewsAPI Everything Endpoint")

st.markdown("""
This application allows you to search for news articles using the [NewsAPI](https://newsapi.org/) `everything` endpoint.
""")

# Sidebar for API Key
st.sidebar.header("🔑 API Key")
api_key = st.sidebar.text_input(
    "Enter your NewsAPI API Key",
    type="password",
    help="Obtain your API key from [NewsAPI](https://newsapi.org/). **Ensure you keep it secure!**",
)

# Calculate default dates
today = datetime.today().date()
default_to_date = today
default_from_date = today - timedelta(days=120)

# Main form for parameters
st.header("🔍 Search Parameters")

with st.form(key='simplified_newsapi_form'):
    # Query
    q = st.text_input(
        "📌 Keywords (q)",
        value="apple",
        help="Enter keywords or phrases to search for in the article title and body."
    )

    # From Date
    from_date = st.date_input(
        "📅 From Date",
        value=default_from_date,
        min_value=default_from_date,
        max_value=default_to_date,
        help="Start date for fetching articles (YYYY-MM-DD)."
    )

    # To Date
    to_date = st.date_input(
        "📅 To Date",
        value=default_to_date,
        min_value=from_date,
        max_value=today,
        help="End date for fetching articles (YYYY-MM-DD)."
    )

    # Sort By
    sort_by = st.selectbox(
        "🔄 Sort By",
        options=["publishedAt", "relevancy", "popularity"],
        index=2,  # Default to 'popularity'
        help="Sort articles by 'publishedAt', 'relevancy', or 'popularity'."
    )

    # Submit Button
    submit_button = st.form_submit_button(label='Fetch Articles')

if submit_button:
    if not api_key:
        st.error("🚫 Please enter your API key in the sidebar to proceed.")
    else:
        # Prepare parameters
        params = {
            "apiKey": api_key,
            "q": q,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "sortBy": sort_by,
            "language": "it",  # Default language set to Italian
            "pageSize": 20,     # Default page size
            "page": 1           # Default to first page
        }

        # Make the API request
        with st.spinner("🔄 Fetching articles..."):
            try:
                response = requests.get("https://newsapi.org/v2/everything", params=params)
                response.raise_for_status()  # Raise HTTPError for bad responses
                data =
