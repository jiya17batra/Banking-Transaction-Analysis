"""
app.py
Banking Transaction Analysis & Fraud Detection — Streamlit App

Deploy on Streamlit Community Cloud:
  1. Push this repo to GitHub (include data/ and assets/ folders)
  2. Go to https://share.streamlit.io -> "New app"
  3. Point it at this repo, branch, and set main file path to "app.py"

Run locally:
  pip install -r requirements.txt
  streamlit run app.py
"""

import os
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Banking Transaction Analysis & Fraud Detection",
                    layout="wide", page_icon="🏦")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "transactions_with_predictions.csv")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, parse_dates=["transaction_date"])
    df.columns = [c.lower() for c in df.columns]
    return df


df = load_data()

st.title("🏦 Banking Transaction Analysis & Fraud Detection")
st.caption(
    "An end-to-end data analytics project — synthetic data generation, cleaning, "
    "SQL analytics, customer behavior analysis, rule-based fraud detection, and "
    "an ML fraud classifier, presented through this interactive dashboard."
)

tab_overview, tab_trends, tab_customers, tab_fraud, tab_data = st.tabs(
    ["📋 Overview", "📈 Trends", "👤 Customer Behavior", "🚨 Fraud Detection", "📊 Raw Data"]
)

# ============================================================
# OVERVIEW TAB
# ============================================================
with tab_overview:
    st.subheader("Project Overview")
    st.markdown("""
This project builds a full analytics pipeline on a synthetic banking transaction
dataset (~60,000 records, 3,000 customers, 2 years of data):

1. **Data Generation** — realistic transaction patterns by merchant category, plus
   intentional data-quality issues (nulls, duplicates, inconsistent formats) and
   embedded fraud patterns.
2. **Data Cleaning** — standardized categories/dates, removed duplicates, handled
   missing values, fixed negative amounts, flagged statistical outliers per category.
3. **SQL Database** — relational schema (`customers`, `transactions`,
   `suspicious_transactions`) with 15+ analytical SQL queries.
4. **Rule-Based Fraud Engine** — 6 weighted rules (high-value, rapid-succession,
   multi-location, spending spikes, high-risk categories, odd-hour transactions).
5. **ML Fraud Model** — Random Forest classifier on engineered features.

**Tech stack:** Python (Pandas, NumPy, Scikit-learn, Plotly), SQL / MySQL, Streamlit
""")

    st.subheader("Key Results")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Transactions Analyzed", f"{len(df):,}")
    c2.metric("Customers", f"{df['customer_id'].nunique():,}")
    c3.metric("Fraud Rate (actual)", f"{100*df['is_fraud'].mean():.2f}%")
    c4.metric("ML Model ROC-AUC", "0.975")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Transaction frequency heatmap (day of week × hour)**")
        st.image(os.path.join(BASE_DIR, "assets", "transaction_heatmap.png"),
                 use_container_width=True)
    with col2:
        st.markdown("**ML model — feature importance**")
        st.image(os.path.join(BASE_DIR, "assets", "feature_importance.png"),
                 use_container_width=True)

    st.markdown("**Fraud model — confusion matrix (test set)**")
    st.image(os.path.join(BASE_DIR, "assets", "confusion_matrix.png"), width=400)

    st.info("Use the **Trends**, **Customer Behavior**, and **Fraud Detection** tabs "
            "to explore the data interactively — filters apply across all tabs.")

# ============================================================
# SIDEBAR FILTERS (apply to Trends / Customers / Fraud tabs)
# ============================================================
st.sidebar.title("🏦 Filters")
date_range = st.sidebar.date_input(
    "Date range",
    value=(df["transaction_date"].min().date(), df["transaction_date"].max().date()),
)
categories = st.sidebar.multiselect("Merchant category", sorted(df["merchant_category"].unique()),
                                     default=list(df["merchant_category"].unique()))
locations = st.sidebar.multiselect("Location", sorted(df["location"].unique()),
                                    default=list(df["location"].unique()))
payment_methods = st.sidebar.multiselect("Payment method", sorted(df["payment_method"].unique()),
                                          default=list(df["payment_method"].unique()))

mask = (
    (df["transaction_date"].dt.date >= date_range[0]) &
    (df["transaction_date"].dt.date <= date_range[1]) &
    (df["merchant_category"].isin(categories)) &
    (df["location"].isin(locations)) &
    (df["payment_method"].isin(payment_methods))
)
fdf = df[mask]

# ============================================================
# TRENDS TAB
# ============================================================
with tab_trends:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Transactions", f"{len(fdf):,}")
    col2.metric("Total Volume (₹)", f"{fdf['transaction_amount'].sum():,.0f}")
    col3.metric("Avg Transaction (₹)", f"{fdf['transaction_amount'].mean():,.2f}")
    col4.metric("Fraud Transactions", f"{int(fdf['is_fraud'].sum()):,}")
    col5.metric("Fraud Rate", f"{100*fdf['is_fraud'].mean():.2f}%")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        monthly = fdf.groupby(fdf["transaction_date"].dt.to_period("M").astype(str)).agg(
            num_transactions=("transaction_id", "count"),
            total_amount=("transaction_amount", "sum")
        ).reset_index().rename(columns={"transaction_date": "month"})
        fig = px.line(monthly, x="month", y="num_transactions", markers=True,
                       title="Monthly Transaction Count")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cat = fdf.groupby("merchant_category")["transaction_amount"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat, x="merchant_category", y="transaction_amount",
                      title="Spending by Merchant Category", color="merchant_category")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        pm = fdf["payment_method"].value_counts().reset_index()
        pm.columns = ["payment_method", "count"]
        fig = px.bar(pm, x="payment_method", y="count", title="Payment Method Usage")
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        loc = fdf.groupby("location")["transaction_amount"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(loc, x="location", y="transaction_amount", title="Location-wise Spending")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# CUSTOMER BEHAVIOR TAB
# ============================================================
with tab_customers:
    spend = fdf[fdf["transaction_type"].isin(["Debit", "Withdrawal", "Transfer"])].groupby("customer_id")["transaction_amount"].sum().reset_index()
    spend.columns = ["customer_id", "total_spent"]
    if len(spend) > 0:
        q1, q3 = spend["total_spent"].quantile([0.33, 0.66])
        spend["segment"] = spend["total_spent"].apply(lambda x: "High" if x >= q3 else ("Medium" if x >= q1 else "Low"))

    c1, c2 = st.columns(2)
    with c1:
        top10 = spend.sort_values("total_spent", ascending=False).head(10)
        fig = px.bar(top10, x="customer_id", y="total_spent", title="Top 10 Customers by Spending")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        seg_counts = spend["segment"].value_counts().reindex(["Low", "Medium", "High"]).reset_index()
        seg_counts.columns = ["segment", "count"]
        fig = px.pie(seg_counts, names="segment", values="count", title="Customer Segmentation")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Spending by Category (per customer)")
    cust_options = sorted(fdf["customer_id"].unique())
    if cust_options:
        sel_cust = st.selectbox("Select customer", cust_options)
        cust_df = fdf[fdf["customer_id"] == sel_cust]
        cat_spend = cust_df[cust_df["transaction_type"].isin(["Debit", "Withdrawal", "Transfer"])].groupby("merchant_category")["transaction_amount"].sum().reset_index()
        fig = px.bar(cat_spend, x="merchant_category", y="transaction_amount", title=f"{sel_cust} - Spending by Category")
        st.plotly_chart(fig, use_container_width=True)

# ============================================================
# FRAUD DETECTION TAB
# ============================================================
with tab_fraud:
    c1, c2 = st.columns(2)
    with c1:
        fraud_counts = fdf["is_fraud"].value_counts().rename({0: "Legitimate", 1: "Fraud"}).reset_index()
        fraud_counts.columns = ["type", "count"]
        fig = px.pie(fraud_counts, names="type", values="count", title="Fraud vs Legitimate", hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cat_fraud = fdf.groupby("merchant_category")["is_fraud"].mean().mul(100).sort_values(ascending=False).reset_index()
        cat_fraud.columns = ["merchant_category", "fraud_rate_pct"]
        fig = px.bar(cat_fraud, x="merchant_category", y="fraud_rate_pct", title="Fraud Rate (%) by Merchant Category")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("High-Value / Suspicious Transactions (> ₹1,00,000)")
    susp = fdf[fdf["transaction_amount"] > 100000].sort_values("transaction_amount", ascending=False)
    show_cols = ["transaction_id", "customer_id", "transaction_date", "transaction_amount",
                  "merchant_category", "location", "is_fraud"]
    if "fraud_probability" in fdf.columns:
        show_cols.append("fraud_probability")
    st.dataframe(susp[show_cols], use_container_width=True)

    if "fraud_probability" in fdf.columns:
        st.subheader("Top ML-Predicted Fraud Risk Transactions")
        top_risk = fdf.sort_values("fraud_probability", ascending=False).head(20)
        st.dataframe(top_risk[["transaction_id", "customer_id", "transaction_date", "transaction_amount",
                                "merchant_category", "fraud_probability", "is_fraud"]],
                      use_container_width=True)

# ============================================================
# RAW DATA TAB
# ============================================================
with tab_data:
    st.dataframe(fdf, use_container_width=True)
    st.download_button("Download filtered data as CSV", fdf.to_csv(index=False),
                        file_name="filtered_transactions.csv")
