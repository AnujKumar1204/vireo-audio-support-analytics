import streamlit as st
from Main import run_analysis, calculate_business_outcome



@st.cache_data
def load_analysis():
    return run_analysis()

ticket, weekly_digest, weekly_agents = load_analysis()
total_contacts, repeat_count, repeat_rate, repeat_cost = calculate_business_outcome(ticket)

weeks = sorted(weekly_digest["weeks"].unique())

select_week = st.selectbox(
    "Select Week",
    weeks
)

week_digest = weekly_digest[
    weekly_digest["weeks"] == select_week
]

week_agents = weekly_agents[
    weekly_agents["weeks"] == select_week
]

st.subheader("Weekly Complaint Digest")

st.dataframe(
    week_digest[["corrected_categories", "ticket_count"]],
    use_container_width=True
)

st.subheader("Weekly Agent Leaderboard")

st.dataframe(
    week_agents[["name", "tickets_closed"]],
    use_container_width=True
)

st.subheader("Business Outcome")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Contacts", total_contacts)
col2.metric("7-Day Repeat Contacts", repeat_count)
col3.metric("Repeat Contact Rate", f"{repeat_rate:.2f}%")
col4.metric("Cost of Repeat Contacts", f"₹{repeat_cost:,.0f}")

