from google.cloud import bigquery
import pandas as pd

client = bigquery.Client(project="sql-study-start2026")
safe_config = bigquery.QueryJobConfig(maximum_bytes_billed=10**9)

def run_and_print(query_text, title):
    print(title)
    try:
        job = client.query(query_text, job_config=safe_config)
        df = job.to_dataframe()
        print(df.to_string(index=False))
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")


# 1. FUNNEL STAGES
query_1 = """
WITH funnel_stages AS (
  SELECT
    COUNT(DISTINCT CASE WHEN event_type = 'home' THEN user_id END) AS stage_1_home,
    COUNT(DISTINCT CASE WHEN event_type = 'department' THEN user_id END) AS stage_2_department,
    COUNT(DISTINCT CASE WHEN event_type = 'product' THEN user_id END) AS stage_3_product,
    COUNT(DISTINCT CASE WHEN event_type = 'cart' THEN user_id END) AS stage_4_cart,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) AS stage_5_purchase
  FROM `bigquery-public-data.thelook_ecommerce.events`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
)
SELECT * FROM funnel_stages;
"""
run_and_print(query_1, "1. FUNNEL STAGES")


# 2. CONVERSION RATES
query_2 = """
WITH funnel_stages AS (
  SELECT
    COUNT(DISTINCT CASE WHEN event_type = 'home' THEN user_id END) AS stage_1_home,
    COUNT(DISTINCT CASE WHEN event_type = 'department' THEN user_id END) AS stage_2_department,
    COUNT(DISTINCT CASE WHEN event_type = 'product' THEN user_id END) AS stage_3_product,
    COUNT(DISTINCT CASE WHEN event_type = 'cart' THEN user_id END) AS stage_4_cart,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) AS stage_5_purchase
  FROM `bigquery-public-data.thelook_ecommerce.events`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
)
SELECT
  stage_1_home,
  stage_2_department,
  stage_3_product,
  stage_4_cart,
  stage_5_purchase,
  ROUND(stage_2_department * 100.0 / stage_1_home, 2) AS home_to_dept_rate,
  ROUND(stage_3_product * 100.0 / stage_2_department, 2) AS dept_to_product_rate,
  ROUND(stage_4_cart * 100.0 / stage_3_product, 2) AS product_to_cart_rate,
  ROUND(stage_5_purchase * 100.0 / stage_4_cart, 2) AS cart_to_purchase_rate,
  ROUND(stage_5_purchase * 100.0 / stage_1_home, 2) AS overall_conversion_rate
FROM funnel_stages;
"""
run_and_print(query_2, "2. CONVERSION RATES")


# 3. FUNNEL BY TRAFFIC SOURCE
query_3 = """
WITH source_funnel AS (
  SELECT
    traffic_source,
    COUNT(DISTINCT CASE WHEN event_type = 'home' THEN user_id END) AS views,
    COUNT(DISTINCT CASE WHEN event_type = 'cart' THEN user_id END) AS cart,
    COUNT(DISTINCT CASE WHEN event_type = 'purchase' THEN user_id END) AS purchases
  FROM `bigquery-public-data.thelook_ecommerce.events`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY traffic_source
)
SELECT
  traffic_source,
  views,
  cart,
  purchases,
  ROUND(cart * 100.0 / NULLIF(views, 0), 2) AS cart_conversion_rate,
  ROUND(purchases * 100.0 / NULLIF(cart, 0), 2) AS purchase_conversion_rate,
  ROUND(purchases * 100.0 / NULLIF(views, 0), 2) AS overall_conversion_rate
FROM source_funnel
ORDER BY purchases DESC;
"""
run_and_print(query_3, "3. FUNNEL BY TRAFFIC SOURCE")


# 4. TIME TO CONVERSION
query_4 = """
WITH user_journey AS (
  SELECT
    user_id,
    MIN(CASE WHEN event_type = 'home' THEN created_at END) AS home_time,
    MIN(CASE WHEN event_type = 'cart' THEN created_at END) AS cart_time,
    MIN(CASE WHEN event_type = 'purchase' THEN created_at END) AS purchase_time
  FROM `bigquery-public-data.thelook_ecommerce.events`
  WHERE created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
  GROUP BY user_id
  HAVING purchase_time IS NOT NULL
)
SELECT
  COUNT(*) AS converted_users,
  ROUND(AVG(TIMESTAMP_DIFF(cart_time, home_time, MINUTE)), 2) AS avg_home_to_cart_min,
  ROUND(AVG(TIMESTAMP_DIFF(purchase_time, cart_time, MINUTE)), 2) AS avg_cart_to_purchase_min,
  ROUND(AVG(TIMESTAMP_DIFF(purchase_time, home_time, MINUTE)), 2) AS avg_total_journey_min
FROM user_journey;
"""
run_and_print(query_4, "4. TIME TO CONVERSION")


# 5. REVENUE METRICS
query_5 = """
WITH revenue_data AS (
  SELECT
    COUNT(DISTINCT o.user_id) AS total_buyers,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(oi.sale_price) AS total_revenue
  FROM `bigquery-public-data.thelook_ecommerce.orders` o
  JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi
    ON o.order_id = oi.order_id
  WHERE o.status = 'Complete'
    AND o.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
)
SELECT
  total_buyers,
  total_orders,
  ROUND(total_revenue, 2) AS total_revenue,
  ROUND(total_revenue / NULLIF(total_orders, 0), 2) AS avg_order_value,
  ROUND(total_revenue / NULLIF(total_buyers, 0), 2) AS revenue_per_buyer
FROM revenue_data;
"""
run_and_print(query_5, "5. REVENUE METRICS")


# 6. TOP CATEGORIES BY REVENUE
query_6 = """
SELECT
  p.category,
  COUNT(DISTINCT oi.order_id) AS total_orders,
  ROUND(SUM(oi.sale_price), 2) AS total_revenue,
  ROUND(AVG(oi.sale_price), 2) AS avg_item_price
FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
JOIN `bigquery-public-data.thelook_ecommerce.products` p
  ON oi.product_id = p.id
JOIN `bigquery-public-data.thelook_ecommerce.orders` o
  ON oi.order_id = o.order_id
WHERE o.status = 'Complete'
  AND o.created_at >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 30 DAY)
GROUP BY p.category
ORDER BY total_revenue DESC
LIMIT 10;
"""
run_and_print(query_6, "6. TOP CATEGORIES BY REVENUE")


# 7. REPEAT BUYERS
query_7 = """
WITH buyer_orders AS (
  SELECT
    user_id,
    COUNT(DISTINCT order_id) AS order_count
  FROM `bigquery-public-data.thelook_ecommerce.orders`
  WHERE status = 'Complete'
  GROUP BY user_id
)
SELECT
  COUNT(*) AS total_buyers,
  COUNTIF(order_count > 1) AS repeat_buyers,
  ROUND(COUNTIF(order_count > 1) * 100.0 / COUNT(*), 2) AS repeat_buyer_rate,
  ROUND(AVG(order_count), 2) AS avg_orders_per_buyer
FROM buyer_orders;
"""
run_and_print(query_7, "7. REPEAT BUYERS")