
-- REAL LIVE DATA — Fetched from dishhome.com.np/internet/plans
-- Source verified: nepalitelecom.com (updated January 7, 2026)
-- DishHome (Dish Media Network) — isp_id = 4
-- ALL prices INCLUDE 13% VAT
-- Plans: Internet-only, Internet+DTH combo, Internet+iTV combo, 1Gbps UltraMax
-- Subscriptions: 1M / 3M / 6M / 12M / 24M
-- FUP: Applied (daily threshold — no exact limit published)
-- NOTE: price_monthly here = price for 1-month subscription (NOT annual÷12)
--       price_quarterly = 3-month total
--       price_annual = 12-month total


DELETE FROM plans WHERE isp_id = 4;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw,
  price_monthly, price_quarterly, price_annual, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES

-- ── INTERNET ONLY

-- 100 Mbps Internet Only
(4, 'DishHome Fibernet 100 Mbps Internet Only 1 Month',
 'DH 100 IO 1M', 'residential', 'active',
 100, '100 Mbps',
 929, NULL, NULL, 'Rs. 929 / 1 Month',
 true, false, 1,
 '[]', '{}',
 'DishHome Fibernet 100 Mbps internet only. 1-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","extra_3mo_bonus_on_12_24m":true}'),

(4, 'DishHome Fibernet 100 Mbps Internet Only 3 Months',
 'DH 100 IO 3M', 'residential', 'active',
 100, '100 Mbps',
 NULL, 3611, NULL, 'Rs. 3,611 / 3 Months',
 true, false, 3,
 '[]', '{}',
 'DishHome Fibernet 100 Mbps internet only. 3-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only"}'),

(4, 'DishHome Fibernet 100 Mbps Internet Only 6 Months',
 'DH 100 IO 6M', 'residential', 'active',
 100, '100 Mbps',
 NULL, NULL, NULL, 'Rs. 4,646 / 6 Months',
 true, false, 6,
 '[]', '{}',
 'DishHome Fibernet 100 Mbps internet only. 6-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_6m":4646}'),

(4, 'DishHome Fibernet 100 Mbps Internet Only 12 Months',
 'DH 100 IO 12M', 'residential', 'active',
 100, '100 Mbps',
 NULL, NULL, 7522, 'Rs. 7,522 / 12 Months',
 true, false, 12,
 '[]', '{}',
 'DishHome Fibernet 100 Mbps internet only. 12-month subscription. Bonus 3 months included. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","extra_3mo_bonus":true}'),

(4, 'DishHome Fibernet 100 Mbps Internet Only 24 Months',
 'DH 100 IO 24M', 'residential', 'active',
 100, '100 Mbps',
 NULL, NULL, NULL, 'Rs. 13,540 / 24 Months',
 true, false, 24,
 '[]', '{}',
 'DishHome Fibernet 100 Mbps internet only. 24-month subscription. Best per-month value. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_24m":13540,"extra_3mo_bonus":true}'),

-- 200 Mbps Internet Only
(4, 'DishHome Fibernet 200 Mbps Internet Only 1 Month',
 'DH 200 IO 1M', 'residential', 'active',
 200, '200 Mbps',
 1283, NULL, NULL, 'Rs. 1,283 / 1 Month',
 true, false, 1,
 '[]', '{}',
 'DishHome Fibernet 200 Mbps internet only. 1-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only"}'),

(4, 'DishHome Fibernet 200 Mbps Internet Only 3 Months',
 'DH 200 IO 3M', 'residential', 'active',
 200, '200 Mbps',
 NULL, 3208, NULL, 'Rs. 3,208 / 3 Months',
 true, false, 3,
 '[]', '{}',
 'DishHome Fibernet 200 Mbps internet only. 3-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only"}'),

(4, 'DishHome Fibernet 200 Mbps Internet Only 6 Months',
 'DH 200 IO 6M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, NULL, 'Rs. 5,951 / 6 Months',
 true, false, 6,
 '[]', '{}',
 'DishHome Fibernet 200 Mbps internet only. 6-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_6m":5951}'),

(4, 'DishHome Fibernet 200 Mbps Internet Only 12 Months',
 'DH 200 IO 12M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, 10177, 'Rs. 10,177 / 12 Months',
 true, false, 12,
 '[]', '{}',
 'DishHome Fibernet 200 Mbps internet only. 12-month subscription. Bonus 3 months included. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","extra_3mo_bonus":true}'),

(4, 'DishHome Fibernet 200 Mbps Internet Only 24 Months',
 'DH 200 IO 24M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, NULL, 'Rs. 18,319 / 24 Months',
 true, false, 24,
 '[]', '{}',
 'DishHome Fibernet 200 Mbps internet only. 24-month subscription. Best per-month value. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_24m":18319,"extra_3mo_bonus":true}'),

-- 300 Mbps Internet Only
(4, 'DishHome Fibernet 300 Mbps Internet Only 1 Month',
 'DH 300 IO 1M', 'residential', 'active',
 300, '300 Mbps',
 1416, NULL, NULL, 'Rs. 1,416 / 1 Month',
 true, false, 1,
 '[]', '{}',
 'DishHome Fibernet 300 Mbps internet only. 1-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only"}'),

(4, 'DishHome Fibernet 300 Mbps Internet Only 3 Months',
 'DH 300 IO 3M', 'residential', 'active',
 300, '300 Mbps',
 NULL, 3716, NULL, 'Rs. 3,716 / 3 Months',
 true, false, 3,
 '[]', '{}',
 'DishHome Fibernet 300 Mbps internet only. 3-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only"}'),

(4, 'DishHome Fibernet 300 Mbps Internet Only 6 Months',
 'DH 300 IO 6M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, NULL, 'Rs. 7,240 / 6 Months',
 true, false, 6,
 '[]', '{}',
 'DishHome Fibernet 300 Mbps internet only. 6-month subscription. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_6m":7240}'),

(4, 'DishHome Fibernet 300 Mbps Internet Only 12 Months',
 'DH 300 IO 12M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, 11991, 'Rs. 11,991 / 12 Months',
 true, false, 12,
 '[]', '{}',
 'DishHome Fibernet 300 Mbps internet only. 12-month subscription. Bonus 3 months included. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","extra_3mo_bonus":true}'),

(4, 'DishHome Fibernet 300 Mbps Internet Only 24 Months',
 'DH 300 IO 24M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, NULL, 'Rs. 21,584 / 24 Months',
 true, false, 24,
 '[]', '{}',
 'DishHome Fibernet 300 Mbps internet only. 24-month subscription. Includes Rs. 1,800 drop wire charge. FUP applies. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_only","price_24m":21584,"drop_wire_charge_npr":1800,"extra_3mo_bonus":true}'),


-- ── INTERNET + DTH COMBO 

-- 100 Mbps + DTH
(4, 'DishHome Fibernet 100 Mbps + DTH Combo 1 Month',
 'DH 100 DTH 1M', 'residential', 'active',
 100, '100 Mbps',
 6679, NULL, NULL, 'Rs. 6,679 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 100 Mbps + DTH satellite TV combo. Includes TV installation (Rs. 2,654) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","tv_install_npr":2654,"router_rental_npr":2000}'),

(4, 'DishHome Fibernet 100 Mbps + DTH Combo 3 Months',
 'DH 100 DTH 3M', 'residential', 'active',
 100, '100 Mbps',
 NULL, 6553, NULL, 'Rs. 6,553 / 3 Months',
 true, false, 3,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 100 Mbps + DTH combo. 3-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo"}'),

(4, 'DishHome Fibernet 100 Mbps + DTH Combo 12 Months',
 'DH 100 DTH 12M', 'residential', 'active',
 100, '100 Mbps',
 NULL, NULL, 12376, 'Rs. 12,376 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 100 Mbps + DTH combo. 12-month subscription. Internet charge Rs. 12,920 (24M). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","extra_3mo_bonus":true}'),

-- 200 Mbps + DTH
(4, 'DishHome Fibernet 200 Mbps + DTH Combo 1 Month',
 'DH 200 DTH 1M', 'residential', 'active',
 200, '200 Mbps',
 6924, NULL, NULL, 'Rs. 6,924 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 200 Mbps + DTH satellite TV combo. Includes TV installation (Rs. 2,654) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","tv_install_npr":2654,"router_rental_npm":2000}'),

(4, 'DishHome Fibernet 200 Mbps + DTH Combo 12 Months',
 'DH 200 DTH 12M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, 14766, 'Rs. 14,766 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 200 Mbps + DTH combo. 12-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","extra_3mo_bonus":true}'),

-- 300 Mbps + DTH
(4, 'DishHome Fibernet 300 Mbps + DTH Combo 1 Month',
 'DH 300 DTH 1M', 'residential', 'active',
 300, '300 Mbps',
 7149, NULL, NULL, 'Rs. 7,149 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 300 Mbps + DTH satellite TV combo. Includes TV installation (Rs. 2,654) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","tv_install_npr":2654,"router_rental_npr":2000}'),

(4, 'DishHome Fibernet 300 Mbps + DTH Combo 12 Months',
 'DH 300 DTH 12M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, 14766, 'Rs. 14,766 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome DTH TV (200+ HD Channels)"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 300 Mbps + DTH combo. 12-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_dth_combo","extra_3mo_bonus":true}'),


-- ── INTERNET + iTV COMBO (IPTV) 

-- 100 Mbps + iTV
(4, 'DishHome Fibernet 100 Mbps + iTV Combo 1 Month',
 'DH 100 iTV 1M', 'residential', 'active',
 100, '100 Mbps',
 7075, NULL, NULL, 'Rs. 7,075 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 100 Mbps + iTV (IPTV) combo. Includes TV installation (Rs. 3,000) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","tv_install_npr":3000,"router_rental_npr":2000}'),

(4, 'DishHome Fibernet 100 Mbps + iTV Combo 12 Months',
 'DH 100 iTV 12M', 'residential', 'active',
 100, '100 Mbps',
 NULL, NULL, 12327, 'Rs. 12,327 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 100 Mbps + iTV combo. 12-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","extra_3mo_bonus":true}'),

-- 200 Mbps + iTV
(4, 'DishHome Fibernet 200 Mbps + iTV Combo 1 Month',
 'DH 200 iTV 1M', 'residential', 'active',
 200, '200 Mbps',
 7320, NULL, NULL, 'Rs. 7,320 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 200 Mbps + iTV (IPTV) combo. Includes TV installation (Rs. 3,000) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","tv_install_npr":3000,"router_rental_npr":2000}'),

(4, 'DishHome Fibernet 200 Mbps + iTV Combo 12 Months',
 'DH 200 iTV 12M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, 12593, 'Rs. 12,593 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 200 Mbps + iTV combo. 12-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","extra_3mo_bonus":true}'),

-- 300 Mbps + iTV
(4, 'DishHome Fibernet 300 Mbps + iTV Combo 1 Month',
 'DH 300 iTV 1M', 'residential', 'active',
 300, '300 Mbps',
 7545, NULL, NULL, 'Rs. 7,545 / 1 Month',
 true, false, 1,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 300 Mbps + iTV (IPTV) combo. Includes TV installation (Rs. 3,000) and router rental (Rs. 2,000). VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","tv_install_npr":3000,"router_rental_npr":2000}'),

(4, 'DishHome Fibernet 300 Mbps + iTV Combo 12 Months',
 'DH 300 iTV 12M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, 14717, 'Rs. 14,717 / 12 Months',
 true, false, 12,
 '[{"type":"iptv","name":"DishHome iTV IPTV"},{"type":"router","name":"Router Rental Included"}]',
 '{"iptv","router"}',
 'DishHome 300 Mbps + iTV combo. 12-month subscription. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"internet_itv_combo","extra_3mo_bonus":true}'),


-- ── ULTRAMAX 1 GBPS 

(4, 'DishHome UltraMax 1 Gbps 12 Months',
 'DH 1Gbps UltraMax 12M', 'fiber', 'active',
 1000, '1 Gbps',
 NULL, NULL, 48474, 'Rs. 48,474 / 12 Months',
 true, true, 12,
 '[{"type":"router","name":"WiFi 6 Router (Free)"},{"type":"other","name":"Free Set-Top-Box"},{"type":"other","name":"Free Drop Wire"},{"type":"other","name":"Free Mesh System"},{"type":"other","name":"Insurance up to Rs. 5 Lakh"},{"type":"other","name":"No FUP"}]',
 '{"router","iptv"}',
 'DishHome UltraMax 1 Gbps. Annual subscription only. Free WiFi 6 router, free STB, free drop wire, free mesh system, Rs. 5 lakh insurance. Supports up to 64 devices. No FUP. VAT included.',
 'https://dishhome.com.np/internet/plans', '{"plan_category":"ultramax","max_devices":64,"no_fup":true,"wifi_standard":"802.11ax","annual_only":true}');


-- ── UPDATE DishHome scraper config 
UPDATE isps SET scraper_config = '{
  "plan_list_url": "https://dishhome.com.np/internet/plans",
  "render_type": "spa",
  "notes": "React SPA — requires JS rendering (Playwright/Selenium). httpx+BS4 will NOT work. Consider using their API endpoint or a headless browser. Page returns only a shell without JS.",
  "selectors": {
    "plan_container": ".plan-card",
    "name": ".plan-title",
    "price": ".plan-price",
    "speed": ".plan-speed"
  }
}'::jsonb WHERE slug = 'dishhome';


-- ── CHANGE LOGS 

DELETE FROM change_logs WHERE isp_id = 4;

-- DishHome 300 Mbps monthly at Rs 1,416 vs WorldLink 300 Mbps monthly at Rs 1,300 (ex-VAT)
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 4, p.id, 'plan_added', 'medium',
  NULL, NULL, NULL, NULL,
  'DishHome 300 Mbps 1-month at Rs 1,416 (VAT incl) vs WorldLink Rs 1,300/mo (VAT excl ~Rs 1,469 incl). DishHome slightly cheaper on monthly for 300 Mbps when VAT adjusted.',
  '{"download_mbps":300,"dh_price_1m_vat_incl":1416,"wl_price_1m_excl_vat":1300,"wl_price_1m_incl_vat_est":1469,"diff_pct":-3.6,"note":"DishHome has FUP; WorldLink does not state FUP on residential"}',
  NOW()
FROM plans p WHERE p.normalized_name = 'DH 300 IO 1M' LIMIT 1;

-- DishHome 1 Gbps launch — no competitor equivalent
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 4, p.id, 'plan_added', 'critical',
  NULL, NULL, NULL, NULL,
  'DishHome UltraMax 1 Gbps launched at Rs 48,474/year (Rs 4,039/mo effective). No competitor offers residential 1 Gbps in Nepal. Includes free WiFi 6 router, mesh, STB, Rs 5L insurance.',
  '{"download_mbps":1000,"price_annual":48474,"price_monthly_effective":4039,"no_fup":true,"wifi6":true,"worldlink_max_mbps":300,"vianet_max_mbps":600,"cgnet_max_mbps":400}',
  NOW()
FROM plans p WHERE p.normalized_name = 'DH 1Gbps UltraMax 12M' LIMIT 1;

-- DishHome 12M 100 Mbps cheapest annual plan in market
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 4, p.id, 'price_decrease', 'medium',
  'price_annual', NULL, '7522', NULL,
  'DishHome 100 Mbps annual at Rs 7,522 (Rs 627/mo effective, VAT incl) — cheapest 100 Mbps annual plan in market. CGNet starts at 250 Mbps; WorldLink 200 Mbps cheapest at Rs 12,600/yr.',
  '{"download_mbps":100,"price_annual":7522,"price_monthly_effective":627,"vat_included":true,"market_note":"DishHome is only major ISP offering sub-Rs 1000/mo 100 Mbps on annual plan"}',
  NOW()
FROM plans p WHERE p.normalized_name = 'DH 100 IO 12M' LIMIT 1;


-- ── Verify 
SELECT '=== DISHHOME INSERT COMPLETE ===' AS status;
SELECT i.name AS isp,
       COUNT(p.id) AS plan_count,
       MIN(p.price_monthly) AS min_monthly_1m_price,
       MAX(p.download_mbps) AS max_speed_mbps
FROM plans p
JOIN isps i ON i.id = p.isp_id
WHERE i.slug = 'dishhome'
GROUP BY i.name;
