-- 1. Total companies
SELECT COUNT(*) AS total_companies
FROM companies;


-- 2. List companies
SELECT id, company_name
FROM companies
ORDER BY company_name;


-- 3. Latest P&L records
SELECT company_id, year, sales, net_profit, eps
FROM profitandloss
ORDER BY year DESC
LIMIT 20;


-- 4. Top companies by sales
SELECT company_id, year, sales
FROM profitandloss
WHERE year = 'Mar 2024'
ORDER BY sales DESC
LIMIT 10;


-- 5. Top companies by net profit
SELECT company_id, year, net_profit
FROM profitandloss
WHERE year = 'Mar 2024'
ORDER BY net_profit DESC
LIMIT 10;


-- 6. Companies with highest ROE
SELECT id, company_name, roe_percentage
FROM companies
WHERE roe_percentage IS NOT NULL
ORDER BY roe_percentage DESC
LIMIT 10;


-- 7. Sector company count
SELECT broad_sector, COUNT(*) AS company_count
FROM sectors
GROUP BY broad_sector
ORDER BY company_count DESC;


-- 8. Companies with less than 5 P&L years
SELECT company_id,
       COUNT(DISTINCT year) AS years_available
FROM profitandloss
WHERE year != 'TTM'
GROUP BY company_id
HAVING COUNT(DISTINCT year) < 5
ORDER BY years_available;


-- 9. Latest market cap
SELECT company_id,
       year,
       market_cap_crore
FROM market_cap
ORDER BY market_cap_crore DESC
LIMIT 10;


-- 10. Join company + financial data
SELECT
    c.company_name,
    p.year,
    p.sales,
    p.net_profit,
    p.eps
FROM companies c
JOIN profitandloss p
    ON c.id = p.company_id
WHERE p.year = 'Mar 2024'
ORDER BY p.net_profit DESC
LIMIT 10;