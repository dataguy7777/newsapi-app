import streamlit as st
import requests
from datetime import datetime, timedelta

# Set the page configuration
st.set_page_config(
    page_title="Simplified NewsAPI Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📢 Simplified NewsAPI Everything Endpoint Explorer")

st.markdown("""
This application allows you to search through articles from various news sources using [NewsAPI](https://newsapi.org/).
""")

# Sidebar for API Key
st.sidebar.header("🔑 API Key")
api_key = st.sidebar.text_input(
    "Enter your NewsAPI API Key",
    type="password",
    help="You can get your API key from [NewsAPI](https://newsapi.org/).",
)

# Calculate default dates
today = datetime.today().date()
default_to_date = today
default_from_date = today - timedelta(days=120)

# Main form for parameters
st.header("🔍 Search Parameters")

with st.form(key='simplified_newsapi_form'):
    # Query
    q = st.text_input("**Keywords (q)**", value="apple", help="""
    Enter keywords or phrases to search for in the article title and body.
    - Surround phrases with quotes ("") for exact match.
    - Use + or - to include or exclude terms.
    - Example: crypto AND (ethereum OR litecoin) NOT bitcoin.
    """)

    # Date Range
    col1, col2 = st.columns(2)
    with col1:
        from_date = st.date_input(
            "**From Date**",
            value=default_from_date,
            min_value=default_from_date,
            max_value=default_to_date,
            help="Oldest article date (YYYY-MM-DD)."
        )
    with col2:
        to_date = st.date_input(
            "**To Date**",
            value=default_to_date,
            min_value=from_date,
            max_value=today,
            help="Newest article date (YYYY-MM-DD)."
        )

    # Sort By
    sort_by = st.selectbox(
        "**Sort By**",
        options=["publishedAt", "relevancy", "popularity"],
        index=0,
        help="Determine the order of the articles."
    )

    # Submit Button
    submit_button = st.form_submit_button(label='Fetch Articles')

if submit_button:
    if not api_key:
        st.error("Please enter your API key in the sidebar.")
    else:
        # Prepare parameters
        params = {
            "apiKey": api_key,
            "q": q,
            "from": from_date.isoformat(),
            "to": to_date.isoformat(),
            "sortBy": sort_by,
            "language": "it",  # Default to Italian
            "pageSize": 20,     # Default page size
            "page": 1           # Default to first page
        }

        # Make the API request
        with st.spinner("Fetching articles..."):
            try:
                response = requests.get("https://newsapi.org/v2/everything", params=params)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)
                data = response.json()

                if data['status'] == 'ok':
                    total_results = data.get('totalResults', 0)
                    articles = data.get('articles', [])

                    st.success(f"Found {total_results} articles.")

                    if articles:
                        for idx, article in enumerate(articles, start=1):
                            st.markdown(f"### {idx}. {article.get('title')}")
                            st.markdown(f"**Source:** {article['source'].get('name')} | **Published At:** {article.get('publishedAt')}")
                            st.markdown(f"{article.get('description')}")
                            st.markdown(f"[Read more]({article.get('url')})")
                            st.markdown("---")
                    else:
                        st.info("No articles found for the given parameters.")
                else:
                    st.error(f"Error: {data.get('message', 'Unknown error')}")
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 426:
                    st.error("HTTP Error 426: Upgrade Required. The server refuses to perform the request using the current protocol but might accept it after the client upgrades to a different protocol.")
                else:
                    st.error(f"HTTP error occurred: {http_err}")
            except Exception as err:
                st.error(f"An error occurred: {err}")

# Footer
st.markdown("---")
st.markdown("""
**Note:** This app uses the [NewsAPI](https://newsapi.org/) `everything` endpoint. Ensure that your API key has the necessary permissions and that you adhere to the usage policies.
""")
