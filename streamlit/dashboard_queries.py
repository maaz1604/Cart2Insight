# ============================================================
# Cart2Insights - Dashboard SQL Query Layer
# ============================================================
#
# Responsibility:
#
#     PostgreSQL
#       ↓
#     SQL Query
#       ↓
#     Pandas DataFrame
#
# This file contains data-access / SQL logic only.
#
# It does NOT contain:
#   - Streamlit UI
#   - Plotly charts
#   - CSS
#   - number formatting
#
# ============================================================

import pandas as pd
from sqlalchemy import text


# ============================================================
# GENERIC DATABASE HELPER
# ============================================================

def fetch_dataframe(
    engine,
    query: str,
) -> pd.DataFrame:
    """
    Execute SQL and return the result as a DataFrame.
    """

    with engine.connect() as connection:

        return pd.read_sql(
            text(query),
            connection,
        )


# ============================================================
# 1. BUSINESS OVERVIEW
# ============================================================

def get_overview_metrics(
    engine,
) -> pd.DataFrame:
    """
    Return headline Overview KPIs.

    Metrics:
        - total revenue
        - total orders
        - AOV
        - total customers
        - total sellers
        - average review score
    """

    query = """
    WITH order_values AS (

        SELECT
            o.order_id,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY
            o.order_id
    ),

    sales_metrics AS (

        SELECT
            SUM(total_order_value)
                AS total_revenue,

            COUNT(*)
                AS total_orders

        FROM order_values
    ),

    customer_metrics AS (

        SELECT
            COUNT(
                DISTINCT customer_unique_id
            ) AS total_customers

        FROM customers
    ),

    seller_metrics AS (

        SELECT
            COUNT(
                DISTINCT seller_id
            ) AS total_sellers

        FROM sellers
    ),

    review_metrics AS (

        SELECT
            AVG(review_score)
                AS average_review_score

        FROM order_reviews
    )

    SELECT

        sales_metrics.total_revenue,

        sales_metrics.total_orders,

        sales_metrics.total_revenue
            / NULLIF(
                sales_metrics.total_orders,
                0
            ) AS aov,

        customer_metrics.total_customers,

        seller_metrics.total_sellers,

        review_metrics.average_review_score

    FROM sales_metrics

    CROSS JOIN customer_metrics
    CROSS JOIN seller_metrics
    CROSS JOIN review_metrics;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 2. SALES ANALYSIS
# ============================================================

def get_monthly_revenue(
    engine,
) -> pd.DataFrame:
    """
    Return monthly revenue and order count.

    Grain:
        one row per month.
    """

    query = """
    WITH order_values AS (

        SELECT

            o.order_id,

            o.order_purchase_timestamp,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY

            o.order_id,

            o.order_purchase_timestamp
    )

    SELECT

        TO_CHAR(
            order_purchase_timestamp,
            'YYYY-MM'
        ) AS month,

        SUM(total_order_value)
            AS revenue,

        COUNT(*) AS orders

    FROM order_values

    GROUP BY

        TO_CHAR(
            order_purchase_timestamp,
            'YYYY-MM'
        )

    ORDER BY
        month;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Revenue by category
# ------------------------------------------------------------

def get_category_revenue(
    engine,
) -> pd.DataFrame:
    """
    Return revenue by product category.

    Translation table is used to return English category
    labels whenever a translation exists.
    """

    query = """
    SELECT

        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category,

        SUM(
            oi.price + oi.freight_value
        ) AS revenue,

        COUNT(
            DISTINCT oi.order_id
        ) AS orders

    FROM order_items AS oi

    LEFT JOIN products AS p
        ON oi.product_id = p.product_id

    LEFT JOIN product_category_name_translation AS t
        ON TRIM(
            p.product_category_name
        ) = TRIM(
            t.product_category_name
        )

    GROUP BY

        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )

    ORDER BY
        revenue DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Top products
# ------------------------------------------------------------

def get_top_products(
    engine,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Return top products by total order value.

    Product names are unavailable in the supplied product
    table, so product_id remains the identifier.
    """

    limit = int(limit)

    query = f"""
    SELECT

        oi.product_id,

        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        ) AS category,

        SUM(
            oi.price + oi.freight_value
        ) AS revenue,

        SUM(
            oi.price
        ) AS product_sales,

        COUNT(*) AS item_units,

        COUNT(
            DISTINCT oi.order_id
        ) AS orders

    FROM order_items AS oi

    LEFT JOIN products AS p
        ON oi.product_id = p.product_id

    LEFT JOIN product_category_name_translation AS t
        ON TRIM(
            p.product_category_name
        ) = TRIM(
            t.product_category_name
        )

    GROUP BY

        oi.product_id,

        COALESCE(
            t.product_category_name_english,
            p.product_category_name,
            'Unknown'
        )

    ORDER BY
        revenue DESC

    LIMIT {limit};
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Sales by customer state
# ------------------------------------------------------------

def get_sales_by_state(
    engine,
) -> pd.DataFrame:
    """
    Return sales performance by customer state.
    """

    query = """
    WITH order_values AS (

        SELECT

            o.order_id,

            o.customer_id,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY

            o.order_id,

            o.customer_id
    )

    SELECT

        c.customer_state AS state,

        SUM(
            ov.total_order_value
        ) AS revenue,

        COUNT(*) AS orders

    FROM order_values AS ov

    INNER JOIN customers AS c
        ON ov.customer_id = c.customer_id

    GROUP BY
        c.customer_state

    ORDER BY
        revenue DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 3. CUSTOMER ANALYSIS
# ============================================================

def get_customer_metrics(
    engine,
) -> pd.DataFrame:
    """
    Return one row per analytical customer.

    Grain:
        customer_unique_id.
    """

    query = """
    WITH order_values AS (

        SELECT

            o.order_id,

            o.customer_id,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY

            o.order_id,

            o.customer_id
    ),

    customer_orders AS (

        SELECT

            c.customer_unique_id,

            COUNT(
                DISTINCT ov.order_id
            ) AS customer_order_count,

            SUM(
                ov.total_order_value
            ) AS customer_total_spending

        FROM order_values AS ov

        INNER JOIN customers AS c
            ON ov.customer_id = c.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        customer_unique_id,

        customer_order_count,

        customer_total_spending,

        customer_total_spending
            / NULLIF(
                customer_order_count,
                0
            ) AS customer_average_order_value,

        CASE

            WHEN customer_order_count > 1
                THEN 'Repeat'

            ELSE 'One-time'

        END AS customer_type

    FROM customer_orders;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Customer distribution
# ------------------------------------------------------------

def get_customer_distribution(
    engine,
) -> pd.DataFrame:
    """
    Return customer count by order-count value.
    """

    query = """
    WITH customer_metrics AS (

        SELECT

            c.customer_unique_id,

            COUNT(
                DISTINCT o.order_id
            ) AS order_count

        FROM customers AS c

        INNER JOIN orders AS o
            ON c.customer_id = o.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        order_count,

        COUNT(*) AS customer_count

    FROM customer_metrics

    GROUP BY
        order_count

    ORDER BY
        order_count;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Customer type distribution
# ------------------------------------------------------------

def get_customer_type_distribution(
    engine,
) -> pd.DataFrame:
    """
    Return One-time vs Repeat customer counts.
    """

    query = """
    WITH customer_orders AS (

        SELECT

            c.customer_unique_id,

            COUNT(
                DISTINCT o.order_id
            ) AS order_count

        FROM customers AS c

        INNER JOIN orders AS o
            ON c.customer_id = o.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        CASE

            WHEN order_count > 1
                THEN 'Repeat'

            ELSE 'One-time'

        END AS customer_type,

        COUNT(*) AS customer_count

    FROM customer_orders

    GROUP BY

        CASE

            WHEN order_count > 1
                THEN 'Repeat'

            ELSE 'One-time'

        END

    ORDER BY
        customer_count DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Customer type spending
# ------------------------------------------------------------

def get_customer_type_spending(
    engine,
) -> pd.DataFrame:
    """
    Compare spending between One-time and Repeat customers.
    """

    query = """
    WITH order_values AS (

        SELECT

            o.order_id,

            o.customer_id,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY

            o.order_id,

            o.customer_id
    ),

    customer_metrics AS (

        SELECT

            c.customer_unique_id,

            COUNT(
                DISTINCT ov.order_id
            ) AS order_count,

            SUM(
                ov.total_order_value
            ) AS total_spending

        FROM order_values AS ov

        INNER JOIN customers AS c
            ON ov.customer_id = c.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        CASE

            WHEN order_count > 1
                THEN 'Repeat'

            ELSE 'One-time'

        END AS customer_type,

        COUNT(*) AS customers,

        AVG(
            total_spending
        ) AS average_spending,

        SUM(
            total_spending
        ) AS total_spending

    FROM customer_metrics

    GROUP BY

        CASE

            WHEN order_count > 1
                THEN 'Repeat'

            ELSE 'One-time'

        END

    ORDER BY
        total_spending DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Top customers
# ------------------------------------------------------------

def get_top_customers(
    engine,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Return highest-spending customers.
    """

    limit = int(limit)

    query = f"""
    WITH order_values AS (

        SELECT

            o.order_id,

            o.customer_id,

            COALESCE(
                SUM(
                    oi.price + oi.freight_value
                ),
                0
            ) AS total_order_value

        FROM orders AS o

        LEFT JOIN order_items AS oi
            ON o.order_id = oi.order_id

        GROUP BY

            o.order_id,

            o.customer_id
    ),

    customer_metrics AS (

        SELECT

            c.customer_unique_id,

            COUNT(
                DISTINCT ov.order_id
            ) AS order_count,

            SUM(
                ov.total_order_value
            ) AS total_spending

        FROM order_values AS ov

        INNER JOIN customers AS c
            ON ov.customer_id = c.customer_id

        GROUP BY
            c.customer_unique_id
    )

    SELECT

        customer_unique_id,

        order_count,

        total_spending

    FROM customer_metrics

    ORDER BY
        total_spending DESC

    LIMIT {limit};
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 4. SELLER & PRODUCT ANALYSIS
# ============================================================

def get_top_sellers(
    engine,
    limit: int = 10,
) -> pd.DataFrame:
    """
    Return top sellers by seller revenue.

    Seller revenue:
        SUM(order_items.price)

    Freight is intentionally excluded.
    """

    limit = int(limit)

    query = f"""
    SELECT

        oi.seller_id,

        SUM(
            oi.price
        ) AS seller_revenue,

        COUNT(
            DISTINCT oi.order_id
        ) AS seller_order_count,

        COUNT(*) AS item_units

    FROM order_items AS oi

    GROUP BY
        oi.seller_id

    ORDER BY
        seller_revenue DESC

    LIMIT {limit};
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Seller performance
# ------------------------------------------------------------

def get_seller_performance(
    engine,
) -> pd.DataFrame:
    """
    Return seller revenue and order count.
    """

    query = """
    SELECT

        oi.seller_id,

        SUM(
            oi.price
        ) AS seller_revenue,

        COUNT(
            DISTINCT oi.order_id
        ) AS seller_order_count

    FROM order_items AS oi

    GROUP BY
        oi.seller_id

    ORDER BY
        seller_revenue DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Seller ratings
# ------------------------------------------------------------

def get_seller_ratings(
    engine,
) -> pd.DataFrame:
    """
    Return average review score associated with each seller.

    Reviews are first reduced to order grain.
    Seller/order pairs are also reduced to one row.
    """

    query = """
    WITH order_review_scores AS (

        SELECT

            order_id,

            AVG(review_score)
                AS order_review_score

        FROM order_reviews

        GROUP BY
            order_id
    ),

    seller_orders AS (

        SELECT DISTINCT

            seller_id,
            order_id

        FROM order_items
    )

    SELECT

        so.seller_id,

        COUNT(
            DISTINCT so.order_id
        ) AS reviewed_orders,

        AVG(
            ors.order_review_score
        ) AS average_review_score

    FROM seller_orders AS so

    INNER JOIN order_review_scores AS ors
        ON so.order_id = ors.order_id

    GROUP BY
        so.seller_id

    ORDER BY
        average_review_score DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 5. DELIVERY ANALYSIS
# ============================================================

def get_delivery_metrics(
    engine,
) -> pd.DataFrame:
    """
    Return overall delivery KPIs.

    Delay rate denominator contains only orders with a known
    delivery outcome.
    """

    query = """
    WITH delivery_data AS (

        SELECT

            order_id,

            CASE

                WHEN order_delivered_customer_date IS NOT NULL

                THEN EXTRACT(
                    EPOCH FROM (
                        order_delivered_customer_date
                        - order_purchase_timestamp
                    )
                ) / 86400.0

            END AS delivery_days,


            CASE

                WHEN order_delivered_customer_date IS NOT NULL
                     AND order_estimated_delivery_date IS NOT NULL

                THEN EXTRACT(
                    EPOCH FROM (
                        order_delivered_customer_date
                        - order_estimated_delivery_date
                    )
                ) / 86400.0

            END AS delivery_delay

        FROM orders
    )

    SELECT

        AVG(
            delivery_days
        ) AS average_delivery_days,


        (
            SUM(
                CASE

                    WHEN delivery_delay > 0
                        THEN 1

                    ELSE 0

                END
            )
            /
            NULLIF(
                SUM(
                    CASE

                        WHEN delivery_delay IS NOT NULL
                            THEN 1

                        ELSE 0

                    END
                ),
                0
            )
        ) * 100 AS delay_rate_known,


        SUM(
            CASE

                WHEN delivery_delay <= 0
                    THEN 1

                ELSE 0

            END
        ) AS on_time_orders,


        SUM(
            CASE

                WHEN delivery_delay > 0
                    THEN 1

                ELSE 0

            END
        ) AS delayed_orders,


        SUM(
            CASE

                WHEN delivery_delay IS NULL
                    THEN 1

                ELSE 0

            END
        ) AS unknown_delivery_orders

    FROM delivery_data;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Delivery status distribution
# ------------------------------------------------------------

def get_delivery_status_distribution(
    engine,
) -> pd.DataFrame:
    """
    Return On Time / Delayed / Unknown order counts.
    """

    query = """
    WITH delivery_data AS (

        SELECT

            order_id,

            CASE

                WHEN order_delivered_customer_date IS NULL
                    THEN 'Unknown'

                WHEN order_delivered_customer_date
                     > order_estimated_delivery_date
                    THEN 'Delayed'

                ELSE 'On Time'

            END AS delivery_status

        FROM orders
    )

    SELECT

        delivery_status,

        COUNT(*) AS order_count

    FROM delivery_data

    GROUP BY
        delivery_status

    ORDER BY

        CASE delivery_status

            WHEN 'On Time' THEN 1

            WHEN 'Delayed' THEN 2

            ELSE 3

        END;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Delivery by state
# ------------------------------------------------------------

def get_delivery_by_state(
    engine,
) -> pd.DataFrame:
    """
    Return delivery performance by customer state.
    """

    query = """
    WITH delivery_data AS (

        SELECT

            o.order_id,

            o.customer_id,

            CASE

                WHEN o.order_delivered_customer_date IS NULL
                    THEN NULL

                WHEN o.order_delivered_customer_date
                     > o.order_estimated_delivery_date
                    THEN 1

                ELSE 0

            END AS is_delayed,

            CASE

                WHEN o.order_delivered_customer_date IS NOT NULL

                THEN EXTRACT(
                    EPOCH FROM (
                        o.order_delivered_customer_date
                        - o.order_purchase_timestamp
                    )
                ) / 86400.0

            END AS delivery_days

        FROM orders AS o
    )

    SELECT

        c.customer_state AS state,

        COUNT(*) AS orders,

        AVG(
            dd.delivery_days
        ) AS average_delivery_days,

        SUM(
            CASE

                WHEN dd.is_delayed = 1
                    THEN 1

                ELSE 0

            END
        ) AS delayed_orders,

        SUM(
            CASE

                WHEN dd.is_delayed IS NOT NULL
                    THEN 1

                ELSE 0

            END
        ) AS orders_with_known_status

    FROM delivery_data AS dd

    INNER JOIN customers AS c
        ON dd.customer_id = c.customer_id

    GROUP BY
        c.customer_state

    ORDER BY
        average_delivery_days DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Delivery vs review
# ------------------------------------------------------------

def get_delivery_vs_review(
    engine,
) -> pd.DataFrame:
    """
    Compare review score between On Time and Delayed orders.
    """

    query = """
    WITH order_review_scores AS (

        SELECT

            order_id,

            AVG(review_score)
                AS review_score

        FROM order_reviews

        GROUP BY
            order_id
    ),

    delivery_data AS (

        SELECT

            order_id,

            CASE

                WHEN order_delivered_customer_date IS NULL
                    THEN NULL

                WHEN order_delivered_customer_date
                     > order_estimated_delivery_date
                    THEN 'Delayed'

                ELSE 'On Time'

            END AS delivery_status

        FROM orders
    )

    SELECT

        dd.delivery_status,

        COUNT(*) AS orders,

        AVG(
            ors.review_score
        ) AS average_review_score,

        STDDEV_SAMP(
            ors.review_score
        ) AS review_score_std

    FROM delivery_data AS dd

    INNER JOIN order_review_scores AS ors
        ON dd.order_id = ors.order_id

    WHERE
        dd.delivery_status IS NOT NULL

    GROUP BY
        dd.delivery_status

    ORDER BY

        CASE dd.delivery_status

            WHEN 'On Time' THEN 1

            WHEN 'Delayed' THEN 2

        END;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 6. CUSTOMER EXPERIENCE
# ============================================================

def get_review_distribution(
    engine,
) -> pd.DataFrame:
    """
    Return review count by review score.
    """

    query = """
    SELECT

        review_score,

        COUNT(*) AS review_count

    FROM order_reviews

    GROUP BY
        review_score

    ORDER BY
        review_score;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Reviews by category
# ------------------------------------------------------------

def get_reviews_by_category(
    engine,
) -> pd.DataFrame:
    """
    Return average review score by category.

    Grain safeguard:
        reviews -> order
        items   -> order + category
        result  -> category
    """

    query = """
    WITH order_review_scores AS (

        SELECT

            order_id,

            AVG(review_score)
                AS review_score

        FROM order_reviews

        GROUP BY
            order_id
    ),

    order_categories AS (

        SELECT DISTINCT

            oi.order_id,

            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category

        FROM order_items AS oi

        LEFT JOIN products AS p
            ON oi.product_id = p.product_id

        LEFT JOIN product_category_name_translation AS t
            ON TRIM(
                p.product_category_name
            ) = TRIM(
                t.product_category_name
            )
    )

    SELECT

        oc.category,

        COUNT(
            DISTINCT oc.order_id
        ) AS reviewed_orders,

        AVG(
            ors.review_score
        ) AS average_review_score

    FROM order_categories AS oc

    INNER JOIN order_review_scores AS ors
        ON oc.order_id = ors.order_id

    GROUP BY
        oc.category

    ORDER BY
        average_review_score DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Rating vs delivery duration
# ------------------------------------------------------------

def get_rating_vs_delivery(
    engine,
) -> pd.DataFrame:
    """
    Return order-level delivery duration and review score.
    """

    query = """
    WITH order_review_scores AS (

        SELECT

            order_id,

            AVG(review_score)
                AS review_score

        FROM order_reviews

        GROUP BY
            order_id
    )

    SELECT

        o.order_id,

        EXTRACT(
            EPOCH FROM (
                o.order_delivered_customer_date
                - o.order_purchase_timestamp
            )
        ) / 86400.0 AS delivery_days,

        ors.review_score

    FROM orders AS o

    INNER JOIN order_review_scores AS ors
        ON o.order_id = ors.order_id

    WHERE
        o.order_delivered_customer_date IS NOT NULL;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 7. PAYMENT ANALYSIS
# ============================================================

def get_payment_distribution(
    engine,
) -> pd.DataFrame:
    """
    Return payment method usage.
    """

    query = """
    SELECT

        payment_type,

        COUNT(*) AS payment_records,

        SUM(
            payment_value
        ) AS payment_value

    FROM order_payments

    GROUP BY
        payment_type

    ORDER BY
        payment_value DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ------------------------------------------------------------
# Payment method vs order status
# ------------------------------------------------------------

def get_payment_status_matrix(
    engine,
) -> pd.DataFrame:
    """
    Return primary payment method by order status.

    Primary payment method:
        payment method with highest aggregated value per order.

    ROW_NUMBER() provides the per-order ranking.
    """

    query = """
    WITH payment_by_type AS (

        SELECT

            order_id,

            payment_type,

            SUM(
                payment_value
            ) AS payment_value

        FROM order_payments

        GROUP BY

            order_id,

            payment_type
    ),

    ranked_payment_methods AS (

        SELECT

            order_id,

            payment_type,

            payment_value,

            ROW_NUMBER() OVER (

                PARTITION BY order_id

                ORDER BY

                    payment_value DESC,

                    payment_type

            ) AS payment_rank

        FROM payment_by_type
    ),

    primary_payment AS (

        SELECT

            order_id,

            payment_type

        FROM ranked_payment_methods

        WHERE
            payment_rank = 1
    )

    SELECT

        pp.payment_type,

        o.order_status,

        COUNT(*) AS order_count

    FROM primary_payment AS pp

    INNER JOIN orders AS o
        ON pp.order_id = o.order_id

    GROUP BY

        pp.payment_type,

        o.order_status

    ORDER BY

        pp.payment_type,

        o.order_status;
    """

    return fetch_dataframe(
        engine,
        query,
    )


# ============================================================
# 8. CATEGORY ORDER-VALUE ANALYSIS
# ============================================================

def get_category_order_values(
    engine,
) -> pd.DataFrame:
    """
    Return one row per order + category.

    This is the correct grain for category-level order-value
    distribution and ANOVA support.
    """

    query = """
    WITH order_category_values AS (

        SELECT

            oi.order_id,

            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'Unknown'
            ) AS category,

            SUM(
                oi.price + oi.freight_value
            ) AS category_order_value

        FROM order_items AS oi

        LEFT JOIN products AS p
            ON oi.product_id = p.product_id

        LEFT JOIN product_category_name_translation AS t
            ON TRIM(
                p.product_category_name
            ) = TRIM(
                t.product_category_name
            )

        GROUP BY

            oi.order_id,

            COALESCE(
                t.product_category_name_english,
                p.product_category_name,
                'Unknown'
            )
    )

    SELECT

        order_id,

        category,

        category_order_value

    FROM order_category_values

    ORDER BY

        category,

        category_order_value DESC;
    """

    return fetch_dataframe(
        engine,
        query,
    )