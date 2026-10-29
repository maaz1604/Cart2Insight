# ============================================================
# Cart2Insights - Dashboard UI Utilities
# ============================================================

import html

import streamlit as st

# ============================================================
# NUMBER / CURRENCY FORMATTERS
# ============================================================


def format_currency(value: float) -> str:
    """
    Format a numeric value as Brazilian currency.

    Examples:
        15843553.24 -> R$15.84M
        15843.24    -> R$15.8K
        159.33      -> R$159.33
    """

    if value is None:
        return "N/A"

    if value >= 1_000_000:
        return f"R${value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"R${value / 1_000:.1f}K"

    return f"R${value:,.2f}"


def format_number(value: float) -> str:
    """
    Format large numbers in a compact dashboard-friendly form.
    """

    if value is None:
        return "N/A"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"

    if value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{value:,.0f}"


def format_percentage(value: float) -> str:
    """
    Format a percentage value.
    """

    if value is None:
        return "N/A"

    return f"{value:.1f}%"


def format_category_name(value: str) -> str:
    """
    Convert database-style category names into readable labels.

    Example:
        health_beauty -> Health Beauty
    """

    if value is None:
        return "Unknown"

    text = str(value).strip()

    if not text:
        return "Unknown"

    # Replace underscores with spaces and capitalize words.
    return text.replace("_", " ").title()


# ============================================================
# KPI CARD
# ============================================================


def kpi_card(
    title: str,
    value: str,
    subtitle: str = "",
) -> None:
    """
    Render a reusable KPI card.

    Parameters
    ----------
    title:
        Metric name.

    value:
        Main metric value.

    subtitle:
        Optional explanatory text.
    """

    safe_title = html.escape(str(title))
    safe_value = html.escape(str(value))
    safe_subtitle = html.escape(str(subtitle))

    subtitle_html = ""

    if subtitle:
        subtitle_html = f"""
        <div class="kpi-subtitle">
            {safe_subtitle}
        </div>
        """

    st.html(f"""
        <style>

        .kpi-card {{
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 16px;
            padding: 20px;
            min-height: 125px;
            box-shadow:
                0 4px 14px rgba(15, 23, 42, 0.05);
            box-sizing: border-box;
        }}

        .kpi-title {{
            color: #64748b;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        .kpi-value {{
            color: #0f172a;
            font-size: 27px;
            font-weight: 700;
            line-height: 1.2;
        }}

        .kpi-subtitle {{
            color: #64748b;
            font-size: 12px;
            line-height: 1.4;
            margin-top: 8px;
        }}

        </style>

        <div class="kpi-card">

            <div class="kpi-title">
                {safe_title}
            </div>

            <div class="kpi-value">
                {safe_value}
            </div>

            {subtitle_html}

        </div>
        """)


# ============================================================
# SECTION HEADER
# ============================================================


def section_header(
    title: str,
    description: str = "",
) -> None:
    """
    Render a consistent dashboard section heading.
    """

    st.markdown(f"## {title}")

    if description:
        st.caption(description)


# ============================================================
# INSIGHT CARD
# ============================================================


def insight_card(
    title: str,
    observation: str,
    interpretation: str,
    business_impact: str,
) -> None:
    """
    Render a business-insight card.

    Structure:
        Observation
        Interpretation
        Business Impact

    This ensures the dashboard communicates findings rather
    than only displaying charts.
    """

    st.html(f"""
        <style>

        .insight-card {{
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-left: 4px solid #2563eb;
            border-radius: 14px;
            padding: 18px 20px;
            margin-top: 12px;
            margin-bottom: 18px;
            box-shadow:
                0 3px 12px rgba(15, 23, 42, 0.04);
        }}

        .insight-title {{
            color: #0f172a;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 12px;
        }}

        .insight-label {{
            color: #475569;
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin-top: 8px;
        }}

        .insight-text {{
            color: #334155;
            font-size: 13px;
            line-height: 1.5;
            margin-top: 3px;
        }}

        </style>

        <div class="insight-card">

            <div class="insight-title">
                {html.escape(title)}
            </div>

            <div class="insight-label">
                Observation
            </div>

            <div class="insight-text">
                {html.escape(observation)}
            </div>

            <div class="insight-label">
                Interpretation
            </div>

            <div class="insight-text">
                {html.escape(interpretation)}
            </div>

            <div class="insight-label">
                Business Impact
            </div>

            <div class="insight-text">
                {html.escape(business_impact)}
            </div>

        </div>
        """)


# ============================================================
# PLOTLY COMMON LAYOUT
# ============================================================


def apply_plotly_theme(
    figure,
    height: int = 400,
) -> None:
    """
    Apply the project's common Plotly visual style.

    Individual charts can still override specific settings.
    """

    figure.update_layout(
        height=height,
        margin=dict(
            l=15,
            r=15,
            t=20,
            b=15,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(
            family="Arial, sans-serif",
            color="#334155",
            size=12,
        ),
        xaxis=dict(
            title=None,
            tickfont=dict(
                color="#334155",
                size=11,
            ),
        ),
        yaxis=dict(
            title=None,
            tickfont=dict(
                color="#334155",
                size=11,
            ),
        ),
        legend=dict(
            font=dict(
                color="#334155",
            ),
        ),
    )
