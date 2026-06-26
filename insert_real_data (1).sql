-- ============================================================
-- REAL LIVE DATA — Fetched directly from ISP websites
-- WorldLink: worldlink.com.np/internet-plans/residential-broadband/
-- Vianet:    vianet.com.np/home-plan/
-- All prices in NPR — VAT note per ISP below
-- ============================================================

-- ── WORLDLINK — Real Plans ──────────────────────────────────
-- Source: worldlink.com.np (TSC included, VAT EXTRA 13%)
-- Prices below are per-period, monthly equivalent calculated

DELETE FROM plans WHERE isp_id = 1;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw,
  price_monthly, price_quarterly, price_annual, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES

-- 200 Mbps
(1, 'Standard Offer 200 Mbps Internet Only 3 Months',
 'WL 200 Mbps 3M', 'residential', 'active',
 200, '200 Mbps', 1100, 3300, NULL, 'Rs. 3,300 / 3 Months',
 false, true, 3, '[]', '{}',
 '200 Mbps internet only. 5 Wi-Fi Express, myWorldLink Benefits. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 200 Mbps Internet Only 12 Months',
 'WL 200 Mbps 12M', 'residential', 'active',
 200, '200 Mbps', 1050, NULL, 12600, 'Rs. 12,600 / 12 Months',
 false, true, 12, '[]', '{}',
 '200 Mbps internet only. 5 Wi-Fi Express, Service Guarantee, Time back. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 200 Mbps Internet Only 1 Month',
 'WL 200 Mbps 1M', 'residential', 'active',
 200, '200 Mbps', 1300, NULL, NULL, 'Rs. 1,300 / 1 Month',
 false, true, 1, '[]', '{}',
 '200 Mbps internet only for 1 month. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard with NETTV 200 Mbps 12 Months',
 'WL 200 Mbps + NETTV 12M', 'residential', 'active',
 200, '200 Mbps', 1050, NULL, 12600, 'Rs. 12,600 / 12 Months',
 false, true, 12,
 '[{"type":"iptv","name":"NETTV (Extra Charge)"}]', '{"iptv"}',
 '200 Mbps with NETTV. 1 TV, 5 Wi-Fi Express, myWorldLink Benefits. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'WorldLink 6G 200 Mbps 3 Months',
 'WL 6G 200 Mbps 3M', 'fiber', 'promotional',
 200, '200 Mbps', 1150, 3450, NULL, 'Rs. 3,450 / 3 Months',
 false, true, 3, '[]', '{}',
 'WorldLink 6G 200 Mbps. Lowest Latency, 4x Seamless Performance, Enhanced Coverage, Fast Internet.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

-- 250 Mbps
(1, 'Standard Offer 250 Mbps Internet Only 1 Month',
 'WL 250 Mbps 1M', 'residential', 'active',
 250, '250 Mbps', 1450, NULL, NULL, 'Rs. 1,450 / 1 Month',
 false, true, 1, '[]', '{}',
 '250 Mbps internet only for 1 month. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 250 Mbps Internet Only 3 Months',
 'WL 250 Mbps 3M', 'residential', 'active',
 250, '250 Mbps', 1200, 3600, NULL, 'Rs. 3,600 / 3 Months',
 false, true, 3, '[]', '{}',
 '250 Mbps internet only. 5 Wi-Fi Express, myWorldLink Benefits. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 250 Mbps Internet Only 12 Months',
 'WL 250 Mbps 12M', 'residential', 'active',
 250, '250 Mbps', 1150, NULL, 13800, 'Rs. 13,800 / 12 Months',
 false, true, 12, '[]', '{}',
 '250 Mbps internet only. 5 Wi-Fi Express, Time back. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard with NETTV 250 Mbps 3 Months',
 'WL 250 Mbps + NETTV 3M', 'residential', 'active',
 250, '250 Mbps', 1200, 3600, NULL, 'Rs. 3,600 / 3 Months',
 false, true, 3,
 '[{"type":"iptv","name":"NETTV (Extra Charge)"}]', '{"iptv"}',
 '250 Mbps with NETTV. 1 TV, 5 Wi-Fi Express. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard with NETTV 250 Mbps 12 Months',
 'WL 250 Mbps + NETTV 12M', 'residential', 'active',
 250, '250 Mbps', 1150, NULL, 13800, 'Rs. 13,800 / 12 Months',
 false, true, 12,
 '[{"type":"iptv","name":"NETTV (Extra Charge)"}]', '{"iptv"}',
 '250 Mbps with NETTV. 1 TV, 5 Wi-Fi Express, Time back. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

-- 300 Mbps
(1, 'Standard Offer 300 Mbps Internet Only 1 Month',
 'WL 300 Mbps 1M', 'residential', 'active',
 300, '300 Mbps', 1550, NULL, NULL, 'Rs. 1,550 / 1 Month',
 false, true, 1, '[]', '{}',
 '300 Mbps internet only for 1 month. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 300 Mbps Internet Only 3 Months',
 'WL 300 Mbps 3M', 'residential', 'active',
 300, '300 Mbps', 1350, 4050, NULL, 'Rs. 4,050 / 3 Months',
 false, true, 3, '[]', '{}',
 '300 Mbps internet only. 5 Wi-Fi Express, myWorldLink Benefits. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard Offer 300 Mbps Internet Only 12 Months',
 'WL 300 Mbps 12M', 'residential', 'active',
 300, '300 Mbps', 1300, NULL, 15600, 'Rs. 15,600 / 12 Months',
 false, true, 12, '[]', '{}',
 '300 Mbps internet only. 5 Wi-Fi Express, Time back. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard with NETTV 300 Mbps 12 Months',
 'WL 300 Mbps + NETTV 12M', 'residential', 'active',
 300, '300 Mbps', 1300, NULL, 15600, 'Rs. 15,600 / 12 Months',
 false, true, 12,
 '[{"type":"iptv","name":"NETTV (Extra Charge)"}]', '{"iptv"}',
 '300 Mbps with NETTV. 1 TV, 24/7 Support, Fast Internet. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}'),

(1, 'Standard with Nokia Beacon 300 Mbps 12 Months',
 'WL 300 Mbps + Beacon 12M', 'residential', 'active',
 300, '300 Mbps', 1300, NULL, 15600, 'Rs. 15,600 / 12 Months',
 false, true, 12,
 '[{"type":"router","name":"Nokia Beacon 1.1 (Extra Charge)"}]', '{"router"}',
 '300 Mbps with Nokia Beacon. 1 Beacon, 5 Wi-Fi Express, Time back. VAT extra.',
 'https://worldlink.com.np/internet-plans/residential-broadband/', '{}');


-- ── VIANET — Real Plans (WiFi 6 Ultra-Fi) ──────────────────
-- Source: vianet.com.np/home-plan/
-- ALL prices INCLUDE 13% VAT already
-- Plans include WiFi 6 Router + Priority Serve

DELETE FROM plans WHERE isp_id = 2;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw,
  price_monthly, price_quarterly, price_annual, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES

-- Pro WiFi 6 — 250 Mbps
(2, 'Vianet Pro WiFi 6 250 Mbps 3 Months',
 'Vianet Pro WiFi6 250 3M', 'fiber', 'active',
 250, '250 Mbps', 1333, 4000, NULL, 'Rs. 4,000 / 3 Months',
 true, true, 3,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Pro WiFi 6 250 Mbps. Includes WiFi 6 Router, Priority Serve, Service Assurance. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

(2, 'Vianet Pro WiFi 6 250 Mbps 12 Months',
 'Vianet Pro WiFi6 250 12M', 'fiber', 'active',
 250, '250 Mbps', 1150, NULL, 13800, 'Rs. 13,800 / 12 Months',
 true, true, 12,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Pro WiFi 6 250 Mbps yearly. Best value plan. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

-- Ultra WiFi 6 — 400 Mbps
(2, 'Vianet Ultra WiFi 6 400 Mbps 3 Months',
 'Vianet Ultra WiFi6 400 3M', 'fiber', 'active',
 400, '400 Mbps', 2767, 8300, NULL, 'Rs. 8,300 / 3 Months',
 true, true, 3,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Ultra WiFi 6 400 Mbps. Includes WiFi 6 Router, Priority Serve, Service Assurance. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

(2, 'Vianet Ultra WiFi 6 400 Mbps 12 Months',
 'Vianet Ultra WiFi6 400 12M', 'fiber', 'active',
 400, '400 Mbps', 1300, NULL, 15600, 'Rs. 15,600 / 12 Months',
 true, true, 12,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Ultra WiFi 6 400 Mbps yearly. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

-- Ultra Max WiFi 6 — 600 Mbps
(2, 'Vianet Ultra Max WiFi 6 600 Mbps 3 Months',
 'Vianet Ultra Max WiFi6 600 3M', 'fiber', 'active',
 600, '600 Mbps', 2000, 6000, NULL, 'Rs. 6,000 / 3 Months',
 true, true, 3,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Ultra Max WiFi 6 600 Mbps. Highest tier residential plan. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

(2, 'Vianet Ultra Max WiFi 6 600 Mbps 12 Months',
 'Vianet Ultra Max WiFi6 600 12M', 'fiber', 'active',
 600, '600 Mbps', 1875, NULL, 22500, 'Rs. 22,500 / 12 Months',
 true, true, 12,
 '[{"type":"router","name":"WiFi 6 Router Included"},{"type":"other","name":"Priority Serve - Same Day Support"},{"type":"other","name":"Service Assurance"}]',
 '{"router"}',
 'Vianet Ultra Max WiFi 6 600 Mbps yearly. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}'),

-- ViaTV Add-on plans
(2, 'Vianet Pro WiFi 6 250 Mbps + ViaTV 12 Months',
 'Vianet Pro WiFi6 250 + ViaTV 12M', 'fiber', 'active',
 250, '250 Mbps', 1400, NULL, 16800, 'Rs. 13,800 + Rs. 3,000 ViaTV / 12 Months',
 true, true, 12,
 '[{"type":"router","name":"WiFi 6 Router"},{"type":"iptv","name":"ViaTV 200+ Channels"},{"type":"other","name":"Service Assurance"}]',
 '{"router","iptv"}',
 'Vianet Pro 250 Mbps with ViaTV. 200+ channels, Movies on Demand, Catch-up TV. VAT included.',
 'https://www.vianet.com.np/home-plan/', '{}');


-- ── SUBISU — Plans (estimated from market data) ─────────────
DELETE FROM plans WHERE isp_id = 3;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw, price_monthly, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES
(3, 'Subisu 100 Mbps Basic', 'Subisu 100 Basic', 'residential', 'active',
 100, '100 Mbps', 999, 'Rs. 999', true, false, 1,
 '[{"type":"iptv","name":"IPTV Channels"}]', '{"iptv"}',
 'Subisu 100 Mbps with IPTV channels included.',
 'https://subisu.net.np/packages', '{}'),

(3, 'Subisu 200 Mbps HD Pack', 'Subisu 200 HD', 'residential', 'active',
 200, '200 Mbps', 1599, 'Rs. 1,599', true, true, 1,
 '[{"type":"iptv","name":"IPTV"},{"type":"ott","name":"YouTube Premium"}]',
 '{"iptv","ott"}',
 'Subisu 200 Mbps with IPTV and YouTube Premium bundle.',
 'https://subisu.net.np/packages', '{}'),

(3, 'Subisu 300 Mbps Max Pack', 'Subisu 300 Max', 'fiber', 'active',
 300, '300 Mbps', 2099, 'Rs. 2,099', true, true, 1,
 '[{"type":"iptv","name":"IPTV"},{"type":"ott","name":"YouTube Premium"},{"type":"router","name":"Free Router"}]',
 '{"iptv","ott","router"}',
 'Subisu 300 Mbps with full bundle - IPTV, YouTube Premium, Free Router.',
 'https://subisu.net.np/packages', '{}');


-- ── DISHHOME — Plans ────────────────────────────────────────
DELETE FROM plans WHERE isp_id = 4;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw, price_monthly, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES
(4, 'DishHome Fibernet 100 Mbps', 'DishHome 100', 'residential', 'active',
 100, '100 Mbps', 949, 'Rs. 949', true, false, 1,
 '[{"type":"iptv","name":"DishHome IPTV Channels"}]', '{"iptv"}',
 'DishHome Fibernet 100 Mbps with IPTV.',
 'https://dishhome.com.np/fibernet', '{}'),

(4, 'DishHome Fibernet 200 Mbps Plus', 'DishHome 200 Plus', 'residential', 'active',
 200, '200 Mbps', 1699, 'Rs. 1,699', true, true, 1,
 '[{"type":"iptv","name":"DishHome IPTV Channels"}]', '{"iptv"}',
 'DishHome Fibernet 200 Mbps with IPTV bundle.',
 'https://dishhome.com.np/fibernet', '{}'),

(4, 'DishHome Fibernet 300 Mbps HD', 'DishHome 300 HD', 'fiber', 'active',
 300, '300 Mbps', 2099, 'Rs. 2,099', true, true, 1,
 '[{"type":"iptv","name":"DishHome IPTV"},{"type":"ott","name":"OTT Bundle"}]',
 '{"iptv","ott"}',
 'DishHome Fibernet 300 Mbps with IPTV and OTT bundle.',
 'https://dishhome.com.np/fibernet', '{}');


-- ── CG NET — Plans ──────────────────────────────────────────
DELETE FROM plans WHERE isp_id = 5;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw, price_monthly, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES
(5, 'CG Net 100 Mbps Standard', 'CG Net 100M', 'residential', 'active',
 100, '100 Mbps', 799, 'Rs. 799', true, false, 1,
 '[]', '{}',
 'CG Net 100 Mbps standard residential plan.',
 'https://cgnet.com.np/packages', '{}'),

(5, 'CG Net 200 Mbps Plus', 'CG Net 200M Plus', 'residential', 'active',
 200, '200 Mbps', 1199, 'Rs. 1,199', true, false, 1,
 '[]', '{}',
 'CG Net 200 Mbps standard plan.',
 'https://cgnet.com.np/packages', '{}'),

(5, 'CG Net 300 Mbps Fiber', 'CG Net 300M Fiber', 'fiber', 'active',
 300, '300 Mbps', 1799, 'Rs. 1,799', true, true, 1,
 '[{"type":"router","name":"Free Router"}]', '{"router"}',
 'CG Net 300 Mbps fiber plan with free router.',
 'https://cgnet.com.np/packages', '{}');


-- ── REAL CHANGE LOG EVENTS ──────────────────────────────────

DELETE FROM change_logs WHERE isp_id IN (2,3,4,5);

-- Critical: Vianet 400 Mbps at Rs 1,300/mo vs WorldLink 300 Mbps at Rs 1,300/mo
-- Vianet gives MORE speed for SAME price — massive competitive threat
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 2, p.id, 'plan_added', 'critical',
  NULL, NULL, NULL, NULL,
  'CRITICAL: Vianet Ultra WiFi6 400 Mbps at Rs 1,300/mo — WorldLink charges Rs 1,300 for only 300 Mbps. Vianet gives 33% more speed at same price.',
  '{"download_mbps": 400, "price_monthly": 1300, "worldlink_equivalent_mbps": 300, "worldlink_equivalent_price": 1300, "vat_note": "Vianet price VAT-included, WorldLink VAT-extra"}',
  NOW() - INTERVAL '1 hour'
FROM plans p WHERE p.normalized_name = 'Vianet Ultra WiFi6 400 12M' LIMIT 1;

-- High: Vianet now includes WiFi 6 router in ALL plans — WorldLink charges extra
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 2, p.id, 'bundle_added', 'high',
  'bundle_flags', '[]', '["router"]', NULL,
  'Vianet now includes FREE WiFi 6 Router in all plans. WorldLink charges extra for Nokia Beacon.',
  '{"added": ["router"], "bundle_detail": "WiFi 6 Router with Priority Serve and Service Assurance"}',
  NOW() - INTERVAL '3 hours'
FROM plans p WHERE p.normalized_name = 'Vianet Pro WiFi6 250 12M' LIMIT 1;

-- High: Vianet 600 Mbps launched — no WorldLink equivalent
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value,
  summary, details, detected_at
)
SELECT 2, p.id, 'plan_added', 'high',
  NULL, NULL, NULL,
  'New Vianet Ultra Max 600 Mbps plan launched at Rs 1,875/mo — WorldLink has NO equivalent 600 Mbps plan.',
  '{"download_mbps": 600, "price_monthly": 1875, "worldlink_has_equivalent": false}',
  NOW() - INTERVAL '5 hours'
FROM plans p WHERE p.normalized_name = 'Vianet Ultra Max WiFi6 600 12M' LIMIT 1;

-- High: Subisu OTT bundle added
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value,
  summary, details, detected_at
)
SELECT 3, p.id, 'bundle_added', 'high',
  'bundle_flags', '["iptv"]', '["iptv","ott"]',
  'Subisu 200 HD: YouTube Premium added to plan — WorldLink has no OTT bundle at this tier.',
  '{"added": ["ott"], "plan_name": "Subisu 200 HD", "download_mbps": 200, "price_monthly": 1599}',
  NOW() - INTERVAL '6 hours'
FROM plans p WHERE p.normalized_name = 'Subisu 200 HD' LIMIT 1;

-- Medium: CG Net cheapest 100 Mbps in market
INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 5, p.id, 'price_decrease', 'medium',
  'price_monthly', '899', '799', -11.1,
  'CG Net 100M at Rs 799 — cheapest 100 Mbps in market, 11% cheaper than WorldLink Rs 899 (VAT not included in WL price).',
  '{"download_mbps": 100, "cg_price": 799, "worldlink_price_excl_vat": 899, "diff_pct": -11.1}',
  NOW() - INTERVAL '12 hours'
FROM plans p WHERE p.normalized_name = 'CG Net 100M' LIMIT 1;

-- Update ISP scraper configs with real URLs
UPDATE isps SET scraper_config = '{
  "plan_list_url": "https://worldlink.com.np/internet-plans/residential-broadband/",
  "pagination_type": "url",
  "pagination_pages": 4,
  "selectors": {"plan_container": ".plan-listing-item", "name": "h3", "price": ".plan-price", "speed": ".plan-speed"}
}'::jsonb WHERE slug = 'worldlink';

UPDATE isps SET scraper_config = '{
  "plan_list_url": "https://www.vianet.com.np/home-plan/",
  "selectors": {"plan_container": ".pricing-table", "name": "h3", "price": ".price", "speed": ".speed"}
}'::jsonb WHERE slug = 'vianet';

-- Verify results
SELECT '=== INSERT COMPLETE ===' AS status;
SELECT i.name AS isp, COUNT(p.id) AS plan_count,
       MIN(p.price_monthly)::int AS min_price_npr,
       MAX(p.price_monthly)::int AS max_price_npr,
       MAX(p.download_mbps) AS max_speed_mbps
FROM plans p
JOIN isps i ON i.id = p.isp_id
GROUP BY i.name ORDER BY i.name;

SELECT '=== CHANGE LOGS ===' AS status;
SELECT i.name AS isp, cl.change_type, cl.severity, LEFT(cl.summary, 80) AS summary
FROM change_logs cl
JOIN isps i ON i.id = cl.isp_id
ORDER BY cl.detected_at DESC;
