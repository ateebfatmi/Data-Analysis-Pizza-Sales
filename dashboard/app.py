import streamlit as st
import pandas as pd
import plotly.express as px

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Pizza Sales Dashboard",
    page_icon="🍕",
    layout="wide"
)

st.title("🍕 Pizza Sales Analytics Dashboard")
st.markdown("---")

# =====================================
# LOAD DATA
# =====================================

@st.cache_data
def load_data():

    orders = pd.read_csv("data/orders.csv")
    order_details = pd.read_csv("data/order_details.csv")
    pizzas = pd.read_csv("data/pizzas.csv")
    pizza_types = pd.read_csv("data/pizza_types.csv")

    orders.columns = orders.columns.str.strip()
    order_details.columns = order_details.columns.str.strip()
    pizzas.columns = pizzas.columns.str.strip()
    pizza_types.columns = pizza_types.columns.str.strip()

    df = (
        order_details
        .merge(pizzas, on="pizza_id")
        .merge(pizza_types, on="pizza_type_id")
        .merge(orders, on="order_id")
    )

    df["revenue"] = df["quantity"] * df["price"]

    return df


df = load_data()

# =====================================
# FIND DATE COLUMN
# =====================================

date_col = None

for col in df.columns:
    if "date" in col.lower():
        date_col = col
        break

if date_col:
    df[date_col] = pd.to_datetime(df[date_col])

# =====================================
# FIND TIME COLUMN
# =====================================

time_col = None

for col in df.columns:
    if "time" in col.lower():
        time_col = col
        break

# =====================================
# SIDEBAR
# =====================================

st.sidebar.header("Filters")

category_filter = st.sidebar.multiselect(
    "Select Category",
    options=df["category"].unique(),
    default=df["category"].unique()
)

size_filter = st.sidebar.multiselect(
    "Select Size",
    options=df["size"].unique(),
    default=df["size"].unique()
)

filtered_df = df[
    (df["category"].isin(category_filter))
    &
    (df["size"].isin(size_filter))
]

# =====================================
# KPI SECTION
# =====================================

total_revenue = filtered_df["revenue"].sum()

total_orders = filtered_df["order_id"].nunique()

total_pizzas = filtered_df["quantity"].sum()

avg_order_value = total_revenue / total_orders

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Revenue",
    f"${total_revenue:,.2f}"
)

col2.metric(
    "Orders",
    f"{total_orders:,}"
)

col3.metric(
    "Pizzas Sold",
    f"{total_pizzas:,}"
)

col4.metric(
    "Avg Order Value",
    f"${avg_order_value:.2f}"
)

st.markdown("---")

# =====================================
# REVENUE BY CATEGORY
# =====================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("Revenue by Category")

    category_revenue = (
        filtered_df.groupby("category")["revenue"]
        .sum()
        .reset_index()
        .sort_values(
            by="revenue",
            ascending=False
        )
    )

    fig = px.bar(
        category_revenue,
        x="category",
        y="revenue",
        color="category"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# REVENUE BY SIZE
# =====================================

with col2:

    st.subheader("Revenue by Pizza Size")

    size_revenue = (
        filtered_df.groupby("size")["revenue"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        size_revenue,
        names="size",
        values="revenue"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# TOP 10 PIZZAS
# =====================================

st.subheader("Top 10 Pizza Types By Revenue")

top10 = (
    filtered_df.groupby("name")["revenue"]
    .sum()
    .reset_index()
    .sort_values(
        by="revenue",
        ascending=False
    )
    .head(10)
)

fig = px.bar(
    top10,
    x="revenue",
    y="name",
    orientation="h",
    color="revenue"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================
# MONTHLY TREND
# =====================================

if date_col:

    st.subheader("Monthly Revenue Trend")

    monthly_revenue = (
        filtered_df.groupby(
            filtered_df[date_col].dt.month
        )["revenue"]
        .sum()
        .reset_index()
    )

    monthly_revenue.columns = [
        "Month",
        "Revenue"
    ]

    fig = px.line(
        monthly_revenue,
        x="Month",
        y="Revenue",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# PEAK ORDERING HOURS
# =====================================

if time_col:

    filtered_df["hour"] = pd.to_datetime(
        filtered_df[time_col].astype(str)
    ).dt.hour

    hourly_orders = (
        filtered_df.groupby("hour")
        .size()
        .reset_index(
            name="orders"
        )
    )

    st.subheader("Peak Ordering Hours")

    fig = px.line(
        hourly_orders,
        x="hour",
        y="orders",
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =====================================
# TOP 3 PIZZAS PER CATEGORY
# =====================================

st.subheader(
    "Top 3 Pizza Types Within Each Category"
)

top_category = (
    filtered_df.groupby(
        ["category", "name"]
    )["revenue"]
    .sum()
    .reset_index()
)

top_category["rank"] = (
    top_category.groupby("category")
    ["revenue"]
    .rank(
        method="dense",
        ascending=False
    )
)

top3 = top_category[
    top_category["rank"] <= 3
]

st.dataframe(
    top3.sort_values(
        ["category", "rank"]
    )
)

# =====================================
# RAW DATA
# =====================================

with st.expander("View Dataset"):

    st.dataframe(
        filtered_df,
        use_container_width=True
    )