import streamlit as st
import pandas as pd
from rules import check_suspicious

st.set_page_config(
    page_title="BankGuard AI",
    page_icon="🏦",
    layout="wide"
)

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
}
.subtitle {
    font-size: 20px;
    color: #9ca3af;
}
.risk-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #111827;
    border: 1px solid #374151;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏦 BankGuard AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Suspicious Transaction Detection Dashboard</div>', unsafe_allow_html=True)

st.write("---")

uploaded_file = st.sidebar.file_uploader("Upload transaction CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_csv("data/transactions.csv")

df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)

risk_scores = []
risk_levels = []
reasons = []

for index, row in df.iterrows():
    score, level, reason = check_suspicious(row)
    risk_scores.append(score)
    risk_levels.append(level)
    reasons.append(reason)

df["risk_score"] = risk_scores
df["risk_level"] = risk_levels
df["reason"] = reasons

st.sidebar.header("🔎 Filters")

risk_filter = st.sidebar.multiselect(
    "Select Risk Level",
    options=["High Risk", "Medium Risk", "Low Risk"],
    default=["High Risk", "Medium Risk", "Low Risk"]
)

transaction_types = sorted(df["transaction_type"].unique())
type_filter = st.sidebar.multiselect(
    "Select Transaction Type",
    options=transaction_types,
    default=transaction_types
)

customer_search = st.sidebar.text_input("Search Customer ID")

min_amount = int(df["amount"].min())
max_amount = int(df["amount"].max())

amount_range = st.sidebar.slider(
    "Amount Range",
    min_value=min_amount,
    max_value=max_amount,
    value=(min_amount, max_amount)
)

filtered_df = df[
    (df["risk_level"].isin(risk_filter)) &
    (df["transaction_type"].isin(type_filter)) &
    (df["amount"] >= amount_range[0]) &
    (df["amount"] <= amount_range[1])
]

if customer_search:
    filtered_df = filtered_df[
        filtered_df["customer_id"].astype(str).str.contains(customer_search, case=False, na=False)
    ]

total_transactions = len(filtered_df)
total_amount = filtered_df["amount"].sum()
high_risk_count = len(filtered_df[filtered_df["risk_level"] == "High Risk"])
medium_risk_count = len(filtered_df[filtered_df["risk_level"] == "Medium Risk"])
low_risk_count = len(filtered_df[filtered_df["risk_level"] == "Low Risk"])

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Transactions", total_transactions)
col2.metric("Total Amount", f"₹{total_amount:,.0f}")
col3.metric("High Risk", high_risk_count)
col4.metric("Safe / Low Risk", low_risk_count)

st.write("---")

left, right = st.columns(2)

with left:
    st.subheader("📊 Risk Level Distribution")
    risk_chart = filtered_df["risk_level"].value_counts().reindex(
        ["High Risk", "Medium Risk", "Low Risk"],
        fill_value=0
    )
    st.bar_chart(risk_chart)

with right:
    st.subheader("💳 Transaction Type Distribution")
    type_chart = filtered_df["transaction_type"].value_counts()
    st.bar_chart(type_chart)

st.write("---")

st.subheader("📋 Transaction Data")
st.dataframe(filtered_df, use_container_width=True)

st.write("---")

high_risk_df = filtered_df[filtered_df["risk_level"] == "High Risk"]

st.subheader("🚨 High Risk Transactions")
if len(high_risk_df) > 0:
    st.dataframe(high_risk_df, use_container_width=True)
else:
    st.success("No high-risk transactions found.")

st.write("---")

st.subheader("🧾 Suspicious Activity Reasons")

reason_df = filtered_df[["transaction_id", "customer_id", "amount", "risk_level", "risk_score", "reason"]]
st.dataframe(reason_df, use_container_width=True)

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Risk Report",
    data=csv,
    file_name="bankguard_ai_dashboard_report.csv",
    mime="text/csv"
)

st.info("BankGuard AI is a rule-based suspicious transaction detection system for educational mini-project use. Do not use real bank data.")