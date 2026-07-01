import express from 'express';
import { BigQuery } from '@google-cloud/bigquery';

const app = express();
const port = process.env.PORT || 3001;

app.use(express.json());

const bigquery = new BigQuery();

app.get('/api/revenue', async (req, res) => {
  const query = `
    SELECT
      revenue_metrics.customer_details.sfdc_account_id AS account_id,
      revenue_metrics.customer_details.child_account_name AS account_name,
      revenue_metrics.customer_details.sub_region AS sub_region,
      revenue_metrics.customer_details.micro_region AS micro_region,
      revenue_metrics.customer_details.industry AS industry,
      revenue_metrics.customer_details.nal_cluster AS cluster,
      CASE
        WHEN (
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_2 IN ('Databases', 'Oracle Database')
          OR
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_3 IN ('GBQ')
        )
        THEN revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_3
        ELSE 'GCP'
      END product_name,
      ROUND(COALESCE(SUM(CASE
        WHEN (
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_2 IN ('Databases', 'Oracle Database')
          OR
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_3 IN ('GBQ')
        )
        AND revenue_metrics.usage_month BETWEEN DATE_TRUNC(CURRENT_DATE(), YEAR) AND LAST_DAY(CURRENT_DATE(), YEAR)
        THEN revenue_metrics.usd_revenue_metrics.invoice_revenue.invoice_revenue
        ELSE 0
      END), 0)) AS db_rev_ytd_current_year
    FROM
      \`concord-prod.service_cloudbi_reporting.revenue_monthly\` AS revenue_metrics
    WHERE
      revenue_metrics.customer_details.region = 'NORTHAM'
      AND revenue_metrics.usage_month BETWEEN DATE_TRUNC(DATE_SUB(CURRENT_DATE(), INTERVAL 1 YEAR), YEAR) AND LAST_DAY(CURRENT_DATE(), YEAR)
    GROUP BY
      account_id,
      account_name,
      sub_region,
      micro_region,
      industry,
      cluster,
      CASE
        WHEN (
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_2 IN ('Databases', 'Oracle Database')
          OR
          revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_3 IN ('GBQ')
        )
        THEN revenue_metrics.product_details.finance_product_hierarchy.finance_product_hierarchy_level_3
        ELSE 'GCP'
      END
    ORDER BY
      db_rev_ytd_current_year DESC
    LIMIT 100
  `;

  try {
    const [rows] = await bigquery.query({ query });
    res.json(rows);
  } catch (error) {
    console.error('Error querying BigQuery:', error);
    res.status(500).json({ error: error.message });
  }
});

app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
