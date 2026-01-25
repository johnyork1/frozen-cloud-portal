import streamlit as st
import pandas as pd
import json
from pathlib import Path

# Load catalog
DATA_DIR = Path(__file__).parent / "data"

def load_catalog():
    catalog_path = DATA_DIR / "catalog.json"
    if catalog_path.exists():
        with open(catalog_path, 'r') as f:
            return json.load(f)
    return {"songs": []}

catalog = load_catalog()

# Page Config
st.set_page_config(page_title="Frozen Cloud Music", page_icon="❄️", layout="wide")

# Title
st.title("❄️ Frozen Cloud Music")
st.caption("Publishing Catalog Portal")

# Sidebar Navigation
page = st.sidebar.radio("Go to", ["Dashboard", "All Songs", "Financials"])

if page == "Dashboard":
    st.header("Catalog Overview")

    songs = catalog['songs']
    total_revenue = sum(s.get('revenue', {}).get('total_earned', 0) for s in songs)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Songs", len(songs))
    col2.metric("Total Revenue", f"${total_revenue:,.2f}")

    # Count by status
    status_counts = {}
    for s in songs:
        status = s.get('status', 'unknown')
        status_counts[status] = status_counts.get(status, 0) + 1
    top_status = max(status_counts, key=status_counts.get) if status_counts else "N/A"
    col3.metric("Most Common Status", top_status.title())

    st.subheader("Recent Songs")
    if songs:
        recent = songs[-10:]
        df = pd.DataFrame(recent)
        cols = ['song_id', 'title', 'artist', 'status']
        display_df = df[[c for c in cols if c in df.columns]]
        st.dataframe(display_df, use_container_width=True)

elif page == "All Songs":
    st.header("📀 Complete Catalog")

    songs = catalog['songs']

    # Get unique artists
    artist_options = ["All"] + sorted(set(s.get('artist', '') for s in songs if s.get('artist')))

    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        artist_filter = st.selectbox("Filter by Artist or Group", artist_options)
    with col2:
        status_filter = st.selectbox("Filter by Status", ["All", "idea", "demo", "mixing", "mastered", "copyright", "released"])
    with col3:
        search = st.text_input("Search by Title or Code")

    # Apply filters
    filtered = songs
    if artist_filter != "All":
        filtered = [s for s in filtered if s.get('artist') == artist_filter]
    if status_filter != "All":
        filtered = [s for s in filtered if s.get('status') == status_filter]
    if search:
        search_lower = search.lower()
        filtered = [s for s in filtered if search_lower in s.get('title', '').lower() or search_lower in s.get('legacy_code', '').lower()]

    st.write(f"**Showing {len(filtered)} of {len(songs)} songs**")

    # Display columns
    if status_filter == "copyright":
        display_cols = ['song_id', 'legacy_code', 'title', 'artist', 'copyright_number']
        col_names = ['Song ID', 'Code', 'Title', 'Artist', 'Copyright #']
    else:
        display_cols = ['song_id', 'legacy_code', 'title', 'artist', 'status']
        col_names = ['Song ID', 'Code', 'Title', 'Artist', 'Status']

    if filtered:
        df = pd.DataFrame(filtered)
        available_cols = [c for c in display_cols if c in df.columns]
        display_df = df[available_cols]
        col_labels = [col_names[display_cols.index(c)] for c in available_cols]
        display_df.columns = col_labels
        st.dataframe(display_df, use_container_width=True, height=500)
    else:
        st.info("No songs match filters")

elif page == "Financials":
    st.header("💰 Revenue Summary")

    songs = catalog['songs']

    # Calculate totals
    total_revenue = sum(s.get('revenue', {}).get('total_earned', 0) for s in songs)
    total_expenses = sum(
        sum(e.get('amount', 0) for e in s.get('revenue', {}).get('expenses', []))
        for s in songs
    )
    net_revenue = total_revenue - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Revenue", f"${total_revenue:,.2f}")
    col2.metric("Total Expenses", f"${total_expenses:,.2f}")
    col3.metric("Net Revenue", f"${net_revenue:,.2f}")

    st.markdown("---")
    st.subheader("Revenue by Song")

    # Songs with revenue
    songs_with_revenue = [
        {
            'title': s['title'],
            'artist': s.get('artist', 'Unknown'),
            'revenue': s.get('revenue', {}).get('total_earned', 0),
            'expenses': sum(e.get('amount', 0) for e in s.get('revenue', {}).get('expenses', []))
        }
        for s in songs
    ]

    # Sort by revenue
    songs_with_revenue.sort(key=lambda x: x['revenue'], reverse=True)

    if songs_with_revenue:
        df = pd.DataFrame(songs_with_revenue)
        df.columns = ['Title', 'Artist', 'Revenue', 'Expenses']
        df['Revenue'] = df['Revenue'].apply(lambda x: f"${x:,.2f}")
        df['Expenses'] = df['Expenses'].apply(lambda x: f"${x:,.2f}")
        st.dataframe(df, use_container_width=True, height=400)
    else:
        st.info("No revenue data yet")

# Footer
st.markdown("---")
st.caption("© 2026 Frozen Cloud Music • Read-Only Portal")
