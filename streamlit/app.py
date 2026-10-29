# ============================================================
# Cart2Insights - Streamlit Dashboard
# ============================================================
#
# Dashboard sections:
#
#   1. Business Overview
#   2. Sales
#   3. Customers
#   4. Sellers & Products
#   5. Delivery
#   6. Customer Experience
#
# Data flow:
#
#       PostgreSQL
#          ↓
#   dashboard_queries.py
#          ↓
#       DataFrame
#          ↓
#        Plotly
#          ↓
#       Streamlit
#
# The dashboard is SQL-backed rather than directly reading CSVs.
# ============================================================


# ============================================================
# IMPORTS
# ============================================================

import sys
from pathlib import Path

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PROJECT PATH SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT MODULES
# ============================================================

from src.db import get_engine

from dashboard_queries import (
    get_category_revenue,
    get_customer_distribution,
    get_customer_metrics,
    get_customer_type_distribution,
    get_customer_type_spending,
    get_delivery_by_state,
    get_delivery_metrics,
    get_delivery_status_distribution,
    get_delivery_vs_review,
    get_monthly_revenue,
    get_overview_metrics,
    get_payment_distribution,
    get_payment_status_matrix,
    get_rating_vs_delivery,
    get_review_distribution,
    get_reviews_by_category,
    get_sales_by_state,
    get_seller_performance,
    get_seller_ratings,
    get_top_customers,
    get_top_products,
    get_top_sellers,
)

from dashboard_utils import (
    apply_plotly_theme,
    format_category_name,
    format_currency,
    format_number,
    format_percentage,
    insight_card,
    kpi_card,
)

# ============================================================
# STREAMLIT PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cart2Insights",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# GLOBAL DASHBOARD CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       APPLICATION
       ======================================================== */

    .stApp {
        background-color: #f6f8fb;
    }


    /* ========================================================
       CONTENT WIDTH
       ======================================================== */

    .block-container {
    max-width: 1450px;
    padding-top: 4rem;
    padding-bottom: 3rem;
}


    /* ========================================================
       SIDEBAR
       ======================================================== */

    [data-testid="stSidebar"] {
        background-color: #111827;
    }

    [data-testid="stSidebar"] * {
        color: #f9fafb;
    }


    /* ========================================================
       MAIN BRAND
       ======================================================== */

    .dashboard-title {
        color: #0f172a;
        font-size: 2.4rem;
        font-weight: 700;
        line-height: 1.1;
        margin-bottom: 4px;
    }

    .dashboard-subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 18px;
    }


    /* ========================================================
       PAGE HEADINGS
       ======================================================== */

    h1,
    h2,
    h3 {
        color: #0f172a !important;
    }


    /* ========================================================
       DATABASE STATUS
       ======================================================== */

    .status-badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 14px;
    }


    /* ========================================================
       GENERAL ELEMENT SPACING
       ======================================================== */

    .stMarkdown h2 {
        margin-top: 0.5rem;
        margin-bottom: 0.35rem;
    }

    .stMarkdown h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.3rem;
    }


    /* ========================================================
       DATAFRAME
       ======================================================== */

    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }


    /* ========================================================
       SELECTBOX / SLIDER
       ======================================================== */

    .stSelectbox,
    .stSlider {
        margin-bottom: 0.5rem;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DATABASE ENGINE
# ============================================================


@st.cache_resource
def get_database_engine():
    """
    Create the SQLAlchemy engine once and reuse it.
    """

    return get_engine()


# ============================================================
# DATABASE CONNECTION
# ============================================================

try:

    engine = get_database_engine()

    with engine.connect() as connection:
        connection.exec_driver_sql("SELECT 1")

    database_connected = True
    connection_error = None

except Exception as exc:

    database_connected = False
    connection_error = exc
    engine = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🛒 Cart2Insights")

    st.caption("Decoding E-Commerce Performance")

    st.divider()

    st.markdown("### Navigation")

    page = st.radio(
        "Go to",
        [
            "Overview",
            "Sales",
            "Customers",
            "Sellers & Products",
            "Delivery",
            "Customer Experience",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### Data Connection")

    if database_connected:

        st.success("PostgreSQL Connected")

    else:

        st.error("PostgreSQL Disconnected")

        st.caption(
            "Check the .env database settings and "
            "make sure PostgreSQL is running."
        )


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="dashboard-title">' "Cart2Insights" "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">' "Decoding E-Commerce Performance" "</div>",
    unsafe_allow_html=True,
)


if database_connected:

    st.markdown(
        """
        <span class="status-badge"
              style="
                  background:#dcfce7;
                  color:#166534;
              ">
            ● Live SQL Data
        </span>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <span class="status-badge"
              style="
                  background:#fee2e2;
                  color:#991b1b;
              ">
            ● Database Unavailable
        </span>
        """,
        unsafe_allow_html=True,
    )

    st.error(f"Unable to connect to PostgreSQL.\n\n" f"Error: {connection_error}")


# ============================================================
# STOP PAGE EXECUTION IF DATABASE IS UNAVAILABLE
# ============================================================

if not database_connected:

    st.warning("The dashboard requires a working PostgreSQL connection.")

    st.stop()


# ============================================================
# ============================================================
# PAGE 1 — BUSINESS OVERVIEW
# ============================================================
# ============================================================

if page == "Overview":

    # --------------------------------------------------------
    # Load Overview KPIs
    # --------------------------------------------------------

    overview = get_overview_metrics(engine)

    metrics = overview.iloc[0]

    # --------------------------------------------------------
    # Page heading
    # --------------------------------------------------------

    st.markdown("## Business Overview")

    st.caption(
        "A high-level view of sales, customers, sellers, " "and customer satisfaction."
    )

    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:

        kpi_card(
            "Total Revenue",
            format_currency(metrics["total_revenue"]),
            "Order value including freight",
        )

    with col2:

        kpi_card(
            "Total Orders",
            format_number(metrics["total_orders"]),
            "All recorded orders",
        )

    with col3:

        kpi_card(
            "Average Order Value",
            format_currency(metrics["aov"]),
            "Revenue ÷ orders",
        )

    with col4:

        kpi_card(
            "Customers",
            format_number(metrics["total_customers"]),
            "Unique customer identities",
        )

    with col5:

        kpi_card(
            "Sellers",
            format_number(metrics["total_sellers"]),
            "Seller records",
        )

    with col6:

        kpi_card(
            "Avg Review Score",
            f'{metrics["average_review_score"]:.2f} / 5',
            "Across recorded reviews",
        )

    # --------------------------------------------------------
    # Load overview charts
    # --------------------------------------------------------

    monthly_revenue = get_monthly_revenue(engine)

    category_revenue = get_category_revenue(engine)

    # --------------------------------------------------------
    # Sales performance
    # --------------------------------------------------------

    st.markdown("## Sales Performance")

    st.caption("Revenue trend and leading product categories.")

    trend_col, category_col = st.columns([1.6, 1])

    # ========================================================
    # Revenue trend
    # ========================================================

    with trend_col:

        st.markdown("### Revenue Trend")

        st.caption("Monthly order value; Sep–Oct 2018 are partial periods.")

        # Remove partial final periods only from the visual.
        trend_data = monthly_revenue[
            ~monthly_revenue["month"].isin(
                [
                    "2018-09",
                    "2018-10",
                ]
            )
        ].copy()

        fig = px.line(
            trend_data,
            x="month",
            y="revenue",
            markers=True,
        )

        fig.update_traces(
            line=dict(
                width=3,
            ),
            marker=dict(
                size=6,
            ),
            hovertemplate=("<b>%{x}</b><br>" "Revenue: R$%{y:,.2f}" "<extra></extra>"),
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_layout(
            hovermode="x unified",
        )

        fig.update_xaxes(
            showgrid=False,
            linecolor="#cbd5e1",
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
            zeroline=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ========================================================
    # Revenue by category
    # ========================================================

    with category_col:

        st.markdown("### Revenue by Category")

        st.caption("Top 10 categories by total order value.")

        category_data = category_revenue.copy()

        category_data["display_category"] = category_data["category"].apply(
            format_category_name
        )

        category_data = (
            category_data.sort_values(
                "revenue",
                ascending=False,
            )
            .head(10)
            .sort_values(
                "revenue",
                ascending=True,
            )
        )

        fig = px.bar(
            category_data,
            x="revenue",
            y="display_category",
            orientation="h",
        )

        fig.update_traces(
            hovertemplate=("<b>%{y}</b><br>" "Revenue: R$%{x:,.2f}" "<extra></extra>"),
            marker_line_width=0,
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
            zeroline=False,
        )

        fig.update_yaxes(
            showgrid=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # Business insight
    # --------------------------------------------------------

    insight_card(
        "Sales Growth & Concentration",
        (
            "Revenue increased strongly through the mature "
            "2017–2018 period, while the leading product "
            "categories account for a substantial share of "
            "sales."
        ),
        (
            "Growth appears primarily volume-driven because "
            "order volume expanded substantially while AOV "
            "remained comparatively stable."
        ),
        (
            "Growth initiatives should continue to focus on "
            "scaling order volume while protecting the strongest "
            "category franchises."
        ),
    )


# ============================================================
# PAGE 2 — SALES
# ============================================================

elif page == "Sales":

    st.markdown("## Sales Analysis")

    st.caption(
        "Detailed view of revenue, products, categories, and " "geographic sales."
    )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    top_n = st.sidebar.slider(
        "Top N Products",
        min_value=5,
        max_value=20,
        value=10,
        step=5,
    )

    # --------------------------------------------------------
    # Load sales datasets
    # --------------------------------------------------------

    monthly_revenue = get_monthly_revenue(engine)

    category_revenue = get_category_revenue(engine)

    top_products = get_top_products(
        engine,
        top_n,
    )

    sales_state = get_sales_by_state(engine)

    # ========================================================
    # Monthly revenue
    # ========================================================

    st.markdown("### Monthly Revenue")

    trend_data = monthly_revenue[
        ~monthly_revenue["month"].isin(
            [
                "2018-09",
                "2018-10",
            ]
        )
    ].copy()

    fig = px.line(
        trend_data,
        x="month",
        y="revenue",
        markers=True,
    )

    fig.update_traces(
        hovertemplate=("<b>%{x}</b><br>" "Revenue: R$%{y:,.2f}" "<extra></extra>")
    )

    apply_plotly_theme(
        fig,
        height=400,
    )

    fig.update_xaxes(
        showgrid=False,
        linecolor="#cbd5e1",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        zeroline=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Category + State
    # ========================================================

    category_col, state_col = st.columns(2)

    # --------------------------------------------------------
    # Category
    # --------------------------------------------------------

    with category_col:

        st.markdown("### Revenue by Category")

        category_data = category_revenue.copy()

        category_data["display_category"] = category_data["category"].apply(
            format_category_name
        )

        category_data = category_data.head(10).sort_values(
            "revenue",
            ascending=True,
        )

        fig = px.bar(
            category_data,
            x="revenue",
            y="display_category",
            orientation="h",
        )

        fig.update_traces(
            hovertemplate=("<b>%{y}</b><br>" "Revenue: R$%{x:,.2f}" "<extra></extra>")
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
        )

        fig.update_yaxes(
            showgrid=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # State
    # --------------------------------------------------------

    with state_col:

        st.markdown("### Sales by State")

        state_data = sales_state.head(10).copy()

        fig = px.bar(
            state_data,
            x="state",
            y="revenue",
        )

        fig.update_traces(
            hovertemplate=("<b>%{x}</b><br>" "Revenue: R$%{y:,.2f}" "<extra></extra>")
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_xaxes(
            showgrid=False,
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ========================================================
    # Top products
    # ========================================================

    st.markdown("### Top Products")

    product_data = top_products.copy()

    product_data["display_category"] = product_data["category"].apply(
        format_category_name
    )

    product_data["product_label"] = (
        product_data["product_id"].str[:8] + " • " + product_data["display_category"]
    )

    product_data = product_data.sort_values(
        "revenue",
        ascending=True,
    )

    fig = px.bar(
        product_data,
        x="revenue",
        y="product_label",
        orientation="h",
    )

    fig.update_traces(
        hovertemplate=("<b>%{y}</b><br>" "Revenue: R$%{x:,.2f}" "<extra></extra>")
    )

    apply_plotly_theme(
        fig,
        height=420,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    fig.update_yaxes(
        showgrid=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    insight_card(
        "Sales Concentration",
        (
            "Sales are concentrated among a relatively small "
            "set of high-revenue categories and are geographically "
            "dominated by São Paulo."
        ),
        (
            "A limited group of categories and locations accounts "
            "for a large share of platform revenue."
        ),
        (
            "Category expansion and geographic growth can be "
            "prioritized around high-performing areas while "
            "testing opportunities in under-penetrated markets."
        ),
    )


# ============================================================
# PAGE 3 — CUSTOMERS
# ============================================================

elif page == "Customers":

    st.markdown("## Customer Analysis")

    st.caption(
        "Customer frequency, spending behaviour, repeat "
        "purchases, and high-value customers."
    )

    # --------------------------------------------------------
    # Load customer datasets
    # --------------------------------------------------------

    customer_metrics = get_customer_metrics(engine)

    customer_distribution = get_customer_distribution(engine)

    customer_type = get_customer_type_distribution(engine)

    customer_spending = get_customer_type_spending(engine)

    top_customers = get_top_customers(
        engine,
        10,
    )

    # --------------------------------------------------------
    # KPI values
    # --------------------------------------------------------

    total_customers = len(customer_metrics)

    repeat_customers = int(customer_metrics["customer_type"].eq("Repeat").sum())

    repeat_rate = repeat_customers / total_customers * 100 if total_customers else 0

    median_spending = customer_metrics["customer_total_spending"].median()

    # --------------------------------------------------------
    # KPI cards
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        kpi_card(
            "Customers",
            format_number(total_customers),
            "Analytical customer identities",
        )

    with col2:

        kpi_card(
            "Repeat Customers",
            format_number(repeat_customers),
            "Customers with >1 order",
        )

    with col3:

        kpi_card(
            "Repeat Rate",
            format_percentage(repeat_rate),
            "Share of customers",
        )

    with col4:

        kpi_card(
            "Median Spending",
            format_currency(median_spending),
            "Typical cumulative spending",
        )

    # ========================================================
    # Customer distribution
    # ========================================================

    distribution_col, type_col = st.columns(2)

    # --------------------------------------------------------
    # Order-count distribution
    # --------------------------------------------------------

    with distribution_col:

        st.markdown("### Customer Order Distribution")

        fig = px.bar(
            customer_distribution,
            x="order_count",
            y="customer_count",
        )

        fig.update_traces(
            hovertemplate=(
                "Orders: <b>%{x}</b><br>" "Customers: %{y:,.0f}" "<extra></extra>"
            )
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_xaxes(
            showgrid=False,
            title="Number of Orders",
        )

        fig.update_yaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
            title="Customers",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # Repeat vs one-time
    # --------------------------------------------------------

    with type_col:

        st.markdown("### One-time vs Repeat")

        fig = px.pie(
            customer_type,
            names="customer_type",
            values="customer_count",
            hole=0.55,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>" "Customers: %{value:,.0f}" "<extra></extra>"
            ),
        )

        fig.update_layout(
            height=390,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10,
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Arial, sans-serif",
                color="#334155",
            ),
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ========================================================
    # Repeat vs spending
    # ========================================================

    st.markdown("### Customer Type & Spending")

    spending_data = customer_spending.copy()

    fig = px.bar(
        spending_data,
        x="customer_type",
        y="average_spending",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>" "Average Spending: R$%{y:,.2f}" "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=350,
    )

    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Top customers
    # ========================================================

    st.markdown("### Top Customers")

    top_customers_display = top_customers.copy()

    top_customers_display["customer_short_id"] = top_customers_display[
        "customer_unique_id"
    ].str[:10]

    top_customers_display["spending_display"] = top_customers_display[
        "total_spending"
    ].map(lambda value: format_currency(value))

    st.dataframe(
        top_customers_display[
            [
                "customer_short_id",
                "order_count",
                "spending_display",
            ]
        ].rename(
            columns={
                "customer_short_id": "Customer",
                "order_count": "Orders",
                "spending_display": "Total Spending",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    insight_card(
        "Customer Retention Opportunity",
        (
            "The customer base is dominated by one-time buyers, "
            "while repeat customers form a much smaller segment."
        ),
        (
            "Repeat customers have higher typical cumulative "
            "spending, making retention strategically valuable."
        ),
        (
            "Post-purchase engagement, replenishment campaigns, "
            "and targeted loyalty initiatives could focus on "
            "converting first-time buyers into repeat customers."
        ),
    )


# ============================================================
# PAGE 4 — SELLERS & PRODUCTS
# ============================================================

elif page == "Sellers & Products":

    st.markdown("## Sellers & Product Performance")

    st.caption(
        "Seller revenue, order volume, product concentration, "
        "and seller satisfaction."
    )

    # --------------------------------------------------------
    # Controls
    # --------------------------------------------------------

    seller_top_n = st.sidebar.slider(
        "Top N Sellers",
        min_value=5,
        max_value=20,
        value=10,
        step=5,
    )

    # --------------------------------------------------------
    # Load seller datasets
    # --------------------------------------------------------

    top_sellers = get_top_sellers(
        engine,
        seller_top_n,
    )

    seller_performance = get_seller_performance(engine)

    seller_ratings = get_seller_ratings(engine)

    # ========================================================
    # Top sellers
    # ========================================================

    st.markdown("### Top Sellers by Revenue")

    seller_data = top_sellers.sort_values(
        "seller_revenue",
        ascending=True,
    )

    seller_data["seller_label"] = "Seller " + seller_data["seller_id"].str[:8]

    fig = px.bar(
        seller_data,
        x="seller_revenue",
        y="seller_label",
        orientation="h",
    )

    fig.update_traces(
        hovertemplate=("<b>%{y}</b><br>" "Revenue: R$%{x:,.2f}" "<extra></extra>")
    )

    apply_plotly_theme(
        fig,
        height=420,
    )

    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    fig.update_yaxes(
        showgrid=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Seller revenue vs orders
    # ========================================================

    st.markdown("### Seller Revenue vs Order Volume")

    seller_scatter = seller_performance.copy()

    seller_scatter["seller_label"] = seller_scatter["seller_id"].str[:8]

    fig = px.scatter(
        seller_scatter,
        x="seller_order_count",
        y="seller_revenue",
        hover_name="seller_label",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>Seller %{hovertext}</b><br>"
            "Orders: %{x:,.0f}<br>"
            "Revenue: R$%{y:,.2f}"
            "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=430,
    )

    fig.update_xaxes(
        title="Seller Order Count",
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    fig.update_yaxes(
        title="Seller Revenue",
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Seller ratings
    # ========================================================

    st.markdown("### Seller Ratings")

    rating_table = seller_ratings.copy()

    # Avoid ranking sellers with extremely small numbers of
    # reviewed orders as if their rating were equally reliable.
    rating_table = rating_table[rating_table["reviewed_orders"] >= 20].head(10)

    rating_table["seller_id"] = rating_table["seller_id"].str[:10]

    rating_table["average_review_score"] = rating_table["average_review_score"].round(2)

    st.dataframe(
        rating_table[
            [
                "seller_id",
                "reviewed_orders",
                "average_review_score",
            ]
        ].rename(
            columns={
                "seller_id": "Seller",
                "reviewed_orders": "Reviewed Orders",
                "average_review_score": "Avg Review",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    insight_card(
        "Seller Performance",
        (
            "Seller revenue is unevenly distributed, with a small "
            "high-value seller group and a long tail of smaller sellers."
        ),
        (
            "Order volume is positively associated with revenue, "
            "although sellers differ in the value generated per order."
        ),
        (
            "Seller management can prioritize high-value partners "
            "while identifying smaller sellers with potential to scale."
        ),
    )


# ============================================================
# PAGE 5 — DELIVERY
# ============================================================

elif page == "Delivery":

    st.markdown("## Delivery Analysis")

    st.caption(
        "Delivery speed, reliability, geographic differences, "
        "and customer satisfaction."
    )

    # --------------------------------------------------------
    # Load data
    # --------------------------------------------------------

    delivery_metrics = get_delivery_metrics(engine).iloc[0]

    delivery_status = get_delivery_status_distribution(engine)

    delivery_state = get_delivery_by_state(engine)

    delivery_review = get_delivery_vs_review(engine)

    # ========================================================
    # Delivery KPI cards
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        kpi_card(
            "Avg Delivery Time",
            (f'{delivery_metrics["average_delivery_days"]:.1f} days'),
            "Orders with actual delivery",
        )

    with col2:

        kpi_card(
            "Delay Rate",
            format_percentage(delivery_metrics["delay_rate_known"]),
            "Known delivery outcomes",
        )

    with col3:

        kpi_card(
            "On-time Orders",
            format_number(delivery_metrics["on_time_orders"]),
            "Delivered on or before estimate",
        )

    with col4:

        kpi_card(
            "Delayed Orders",
            format_number(delivery_metrics["delayed_orders"]),
            "Delivered after estimate",
        )

    # ========================================================
    # Delivery status
    # ========================================================

    status_col, state_col = st.columns(2)

    # --------------------------------------------------------
    # Status chart
    # --------------------------------------------------------

    with status_col:

        st.markdown("### Delivery Status")

        fig = px.pie(
            delivery_status,
            names="delivery_status",
            values="order_count",
            hole=0.55,
        )

        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            hovertemplate=(
                "<b>%{label}</b><br>" "Orders: %{value:,.0f}" "<extra></extra>"
            ),
        )

        fig.update_layout(
            height=390,
            margin=dict(
                l=10,
                r=10,
                t=10,
                b=10,
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(
                family="Arial, sans-serif",
                color="#334155",
            ),
            showlegend=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # --------------------------------------------------------
    # State delivery performance
    # --------------------------------------------------------

    with state_col:

        st.markdown("### Delivery Performance by State")

        state_data = delivery_state.copy()

        state_data["delay_rate"] = (
            state_data["delayed_orders"] / state_data["orders_with_known_status"] * 100
        )

        # Exclude very small states from the visual so the
        # ranking is not dominated by tiny samples.
        state_data = (
            state_data[state_data["orders_with_known_status"] >= 100]
            .sort_values(
                "delay_rate",
                ascending=False,
            )
            .head(10)
        )

        fig = px.bar(
            state_data,
            x="delay_rate",
            y="state",
            orientation="h",
        )

        fig.update_traces(
            hovertemplate=("<b>%{y}</b><br>" "Delay Rate: %{x:.1f}%" "<extra></extra>")
        )

        apply_plotly_theme(
            fig,
            height=390,
        )

        fig.update_xaxes(
            showgrid=True,
            gridcolor="#e2e8f0",
            title="Delay Rate",
        )

        fig.update_yaxes(
            showgrid=False,
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ========================================================
    # Delivery vs review
    # ========================================================

    st.markdown("### Delivery Status vs Review Score")

    fig = px.bar(
        delivery_review,
        x="delivery_status",
        y="average_review_score",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>" "Average Review: %{y:.2f} / 5" "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=350,
    )

    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_yaxes(
        range=[0, 5],
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    insight_card(
        "Delivery & Customer Satisfaction",
        (
            "Most orders with known delivery outcomes are on time, "
            "but delayed orders receive substantially lower review scores."
        ),
        (
            "Delivery reliability appears strongly associated with "
            "customer satisfaction in the observed data."
        ),
        (
            "Reducing delivery delays should be treated as a customer "
            "experience initiative as well as an operational objective."
        ),
    )


# ============================================================
# PAGE 6 — CUSTOMER EXPERIENCE
# ============================================================

elif page == "Customer Experience":

    st.markdown("## Customer Experience")

    st.caption(
        "Review distribution, category satisfaction, and the "
        "relationship between delivery and customer ratings."
    )

    # --------------------------------------------------------
    # Load experience datasets
    # --------------------------------------------------------

    review_distribution = get_review_distribution(engine)

    reviews_category = get_reviews_by_category(engine)

    delivery_review = get_delivery_vs_review(engine)

    rating_delivery = get_rating_vs_delivery(engine)

    # ========================================================
    # Review distribution
    # ========================================================

    st.markdown("### Review Score Distribution")

    fig = px.bar(
        review_distribution,
        x="review_score",
        y="review_count",
    )

    fig.update_traces(
        hovertemplate=("Score: <b>%{x}</b><br>" "Reviews: %{y:,.0f}" "<extra></extra>")
    )

    apply_plotly_theme(
        fig,
        height=350,
    )

    fig.update_xaxes(
        dtick=1,
        showgrid=False,
        title="Review Score",
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        title="Reviews",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Category reviews
    # ========================================================

    st.markdown("### Reviews by Category")

    category_review_data = reviews_category.copy()

    category_review_data["display_category"] = category_review_data["category"].apply(
        format_category_name
    )

    category_review_data = category_review_data.sort_values(
        "average_review_score",
        ascending=True,
    )

    fig = px.bar(
        category_review_data.head(10),
        x="average_review_score",
        y="display_category",
        orientation="h",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>" "Average Review: %{x:.2f} / 5" "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=430,
    )

    fig.update_xaxes(
        range=[0, 5],
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    fig.update_yaxes(
        showgrid=False,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Delivery status vs review
    # ========================================================

    st.markdown("### Delivery Status & Satisfaction")

    fig = px.bar(
        delivery_review,
        x="delivery_status",
        y="average_review_score",
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{x}</b><br>" "Average Review: %{y:.2f} / 5" "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=350,
    )

    fig.update_xaxes(
        showgrid=False,
    )

    fig.update_yaxes(
        range=[0, 5],
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    # ========================================================
    # Delivery duration vs rating
    # ========================================================

    st.markdown("### Delivery Duration vs Review Score")

    # A scatter plot containing every row can become visually
    # dense, so sample a maximum of 5,000 observations.
    scatter_data = rating_delivery.sample(
        min(
            len(rating_delivery),
            5000,
        ),
        random_state=42,
    )

    fig = px.scatter(
        scatter_data,
        x="delivery_days",
        y="review_score",
        opacity=0.45,
    )

    fig.update_traces(
        hovertemplate=(
            "Delivery: %{x:.1f} days<br>" "Review: %{y:.1f} / 5" "<extra></extra>"
        )
    )

    apply_plotly_theme(
        fig,
        height=420,
    )

    fig.update_xaxes(
        title="Delivery Days",
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    fig.update_yaxes(
        title="Review Score",
        range=[0.5, 5.5],
        dtick=1,
        showgrid=True,
        gridcolor="#e2e8f0",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    insight_card(
        "Customer Experience",
        (
            "Review scores are concentrated toward 5 stars, but "
            "a meaningful low-rating segment remains."
        ),
        (
            "Delivery reliability shows a much larger satisfaction "
            "difference than simple delivery duration alone."
        ),
        (
            "Customer-experience improvement should prioritize "
            "reliable promised-date performance rather than only "
            "reducing average delivery duration."
        ),
    )
