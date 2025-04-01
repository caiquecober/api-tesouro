import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Tesouro CKAN Explorer por Caíque Cober", layout="wide")

st.title("📊 Tesouro Transparente CKAN Explorer")
st.markdown("Explore and share open data packages from the Brazilian Treasury CKAN API.")

# Sidebar filters
st.sidebar.header("🔍 Search Filters")
query = st.sidebar.text_input("Search term (e.g. dívida)", value="divida")

file_type = st.sidebar.selectbox("Filter by file type (optional)", options=["", "CSV", "XLS", "JSON", "PDF"], index=0)
file_type = file_type.lower() if file_type else None

modified_within_days = st.sidebar.slider("Modified within the last N days", min_value=0, max_value=180, value=60)

max_results = st.sidebar.number_input("Max results", min_value=10, max_value=500, value=100, step=10)

# Function to fetch and filter CKAN data
@st.cache_data
def search_ckan_datasets(base_url, query, file_type=None, modified_within_days=None, max_results=100):
    url = f"{base_url}?q={query}&rows={max_results}"
    response = requests.get(url)
    data = response.json()

    if not data.get("success"):
        return []

    cutoff_date = None
    if modified_within_days:
        cutoff_date = datetime.now() - timedelta(days=modified_within_days)

    results = []
    for result in data["result"]["results"]:
        # Filter by last modified
        mod_date = datetime.fromisoformat(result["metadata_modified"])
        if cutoff_date and mod_date < cutoff_date:
            continue

        # Filter by file type
        resources = result.get("resources", [])
        if file_type:
            resources = [r for r in resources if r.get("format", "").lower() == file_type.lower()]

        if resources:
            results.append({
                "title": result["title"],
                "last_modified": result["metadata_modified"],
                "resources": [
                    {"name": r["name"], "url": r["url"], "format": r["format"]}
                    for r in resources
                ]
            })

    return results

# Call function
base_api = "http://www.tesourotransparente.gov.br/ckan/api/3/action/package_search"
datasets = search_ckan_datasets(base_api, query=query, file_type=file_type, modified_within_days=modified_within_days, max_results=max_results)

# Display results
st.markdown(f"### 📁 Found {len(datasets)} datasets")
for d in datasets:
    st.markdown(f"#### 📦 {d['title']}")
    st.caption(f"Last Modified: {d['last_modified']}")
    for res in d["resources"]:
        st.markdown(f"- [{res['name']}]({res['url']}) ({res['format']})")
    st.markdown("---")
