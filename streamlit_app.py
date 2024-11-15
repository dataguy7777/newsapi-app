import streamlit as st
import requests
from datetime import datetime, timedelta
from urllib.parse import urlencode

# Set the page configuration
st.set_page_config(
    page_title="NewsAPI Everything Endpoint",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📢 NewsAPI Everything Endpoint Explorer")

st.markdown("""
This application allows you to search through millions of articles from over 150,000 news sources and blogs using [NewsAPI](https://newsapi.org/).
""")

# Sidebar for API Key
st.sidebar.header("🔑 API Key")
api_key = st.sidebar.text_input(
    "Enter your NewsAPI API Key",
    type="password",
    help="You can get your API key from [NewsAPI](https://newsapi.org/).",
)

# Function to fetch available sources (for the 'sources' parameter)
@st.cache_data
def get_sources(api_key):
    url = "https://newsapi.org/v2/sources"
    params = {"apiKey": api_key}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data['status'] == 'ok':
            return sorted([source['id'] for source in data['sources']])
    return []

# Calculate default dates
today = datetime.today().date()
default_to_date = today
default_from_date = today - timedelta(days=120)

# Main form for parameters
st.header("🔍 Search Parameters")

with st.form(key='newsapi_form'):
    # Query
    q = st.text_input("**Keywords (q)**", help="""
    Enter keywords or phrases to search for in the article title and body.
    - Surround phrases with quotes ("") for exact match.
    - Use + or - to include or exclude terms.
    - Example: crypto AND (ethereum OR litecoin) NOT bitcoin.
    """)

    # Search In
    search_in = st.multiselect(
        "**Search In**",
        options=["title", "description", "content"],
        help="Select the fields to restrict your search to."
    )

    # Sources
    if api_key:
        sources_list = get_sources(api_key)
        sources = st.multiselect(
            "**Sources**",
            options=sources_list,
            help="Select news sources to include."
        )
    else:
        sources = st.multiselect(
            "**Sources**",
            options=[],
            disabled=True,
            help="Enter your API key to select sources."
        )

    # Domains
    domains = st.text_input(
        "**Domains**",
        help="Comma-separated domains (e.g., bbc.co.uk, techcrunch.com) to restrict the search to."
    )

    # Exclude Domains
    exclude_domains = st.text_input(
        "**Exclude Domains**",
        help="Comma-separated domains (e.g., bbc.co.uk, techcrunch.com) to exclude from the results."
    )

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

    # Language
    language = st.selectbox(
        "**Language**",
        options=["", "ar", "de", "en", "es", "fr", "he", "it", "nl", "no", "pt", "ru", "se", "ud", "zh"],
        index=7,  # 'it' is the 8th item (0-based index)
        help="Choose the language of the articles."
    )

    # Sort By
    sort_by = st.selectbox(
        "**Sort By**",
        options=["publishedAt", "relevancy", "popularity"],
        index=0,
        help="Determine the order of the articles."
    )

    # Page Size
    page_size = st.number_input(
        "**Page Size**",
        min_value=1,
        max_value=100,
        value=20,
        step=1,
        help="Number of results to return per page (max 100)."
    )

    # Page
    page = st.number_input(
        "**Page Number**",
        min_value=1,
        value=1,
        step=1,
        help="Page number to retrieve."
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
            "q": q if q else None,
            "searchIn": ",".join(search_in) if search_in else None,
            "sources": ",".join(sources) if sources else None,
            "domains": domains if domains else None,
            "excludeDomains": exclude_domains if exclude_domains else None,
            "from": from_date.isoformat() if from_date else None,
            "to": to_date.isoformat() if to_date else None,
            "language": language if language else None,
            "sortBy": sort_by if sort_by else None,
            "pageSize": page_size,
            "page": page,
        }

        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}

        # Make the API request
        with st.spinner("Fetching articles..."):
            response = requests.get("https://newsapi.org/v2/everything", params=params)

        if response.status_code == 200:
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
        else:
            st.error(f"HTTP Error {response.status_code}: Unable to fetch articles.")

# Footer
st.markdown("---")
st.markdown("""
**Note:** This app uses the [NewsAPI](https://newsapi.org/) `everything` endpoint. Ensure that your API key has the necessary permissions and that you adhere to the usage policies.
""")
