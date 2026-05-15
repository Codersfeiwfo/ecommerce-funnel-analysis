# E-Commerce Funnel Analysis — SQL (Google BigQuery)

SQL project for analyzing an e-commerce sales funnel using :contentReference[oaicite:1]{index=1} and the public :contentReference[oaicite:2]{index=2}.

## Project Goals
- Analyze the sales funnel: from first visit to purchase
- Compare marketing channel performance by conversion
- Measure average time to conversion
- Calculate key revenue metrics (AOV, Revenue per Buyer)
- Identify top product categories and repeat buyer rate

---

## Dataset
Source: `bigquery-public-data.thelook_ecommerce`

Tables used:

| Table | Description |
|-------|-------------|
| events | User events (home, product, cart, purchase) |
| orders | Customer orders |
| order_items | Items inside orders |
| products | Product catalog and categories |

---

## Analysis Performed

### 1. Sales Funnel
Tracked unique users across funnel stages:

`Home → Department → Product → Cart → Purchase`

**Insight:** Largest drop-off occurs between **Product** and **Cart**, indicating the main optimization opportunity.

---

### 2. Conversion Rates
Calculated step-by-step and overall conversion rates.

**Insight:** Overall conversion rate reflects total funnel efficiency.

---

### 3. Funnel by Traffic Source
Compared conversion performance across traffic channels.

**Insight:** Email traffic showed the highest conversion despite lower volume.

---

### 4. Time to Conversion
Measured average time from first visit to purchase.

**Insight:** Extremely short or long times may indicate abnormal behavior or UX issues.

---

### 5. Revenue Metrics
Calculated:
- Total Revenue
- Average Order Value (AOV)
- Revenue per Buyer

---

### 6. Top Categories by Revenue
Top 10 categories by total revenue and average item price.

---

### 7. Repeat Buyers Analysis
Measured:
- Repeat buyer rate: **12%**
- Average orders per buyer: **1.13**

---

## Tools
- SQL (Standard SQL)
- Google BigQuery
- Python

---

## How to Run
1. Open [Google BigQuery Console](https://console.cloud.google.com/bigquery?utm_source=chatgpt.com)
2. Copy queries from `ecommerce_analysis.sql`
3. Run them directly
4. Dataset connects automatically (`bigquery-public-data.thelook_ecommerce`)


## Recommendations

Based on the analysis, a few possible improvements are:

- Improve the **Product → Cart** stage, since the biggest drop happens there.
- Focus more on high-converting traffic sources like **Email**.
- Work on customer retention, because repeat buyer rate is only **12%**.
