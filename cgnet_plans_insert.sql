
--  REAL LIVE DATA — Fetched directly from CGNet website
--  CGNet: cgnet.com.np/wifi-six
--  ALL prices INCLUDE 13% VAT already
--  Plans are Wi-Fi 6 (802.11ax) — New Connection Only
--  Hardware: Huawei OptiXstar HG8145X6 (GPON ONT)
--  No FUP on any plan
--  Deposit: Rs. 500 (Internet only)
--  Premium installation: Rs. 3,000 (non-refundable)




DELETE FROM plans WHERE isp_id = 5;

INSERT INTO plans (
  isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw,
  price_monthly, price_quarterly, price_annual, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES
55

(5, 'CGNet Wi-Fi 6 250 Mbps Internet Only 12 Months',
 'CGNet WiFi6 250 12M', 'fiber', 'active',
 250, '250 Mbps',
 1125, NULL, 13499, 'Rs. 13,499 / year',
 true, true, 12,
 '[{"type":"router","name":"Huawei OptiXstar HG8145X6 (Wi-Fi 6 ONT)"},{"type":"other","name":"No FUP"}]',
 '{"router"}',
 'CGNet Wi-Fi 6 250 Mbps. Ideal for ~3-5 active users. Smooth HD/4K streaming, video calls, online learning, casual gaming. No FUP. VAT included.',
 'https://cgnet.com.np/wifi-six', '{"wifi_standard":"802.11ax","max_ap_users":128,"deposit_npr":500,"install_charge_npr":3000,"new_connection_only":true}'),


(5, 'CGNet Wi-Fi 6 350 Mbps Internet Only 12 Months',
 'CGNet WiFi6 350 12M', 'fiber', 'active',
 350, '350 Mbps',
 1167, NULL, 13999, 'Rs. 13,999 / year',
 true, true, 12,
 '[{"type":"router","name":"Huawei OptiXstar HG8145X6 (Wi-Fi 6 ONT)"},{"type":"other","name":"No FUP"},{"type":"other","name":"Smart Home & CCTV Support"}]',
 '{"router"}',
 'CGNet Wi-Fi 6 350 Mbps. Best Value. Built for ~5-8 active users. Multiple 4K streams, smooth online gaming, smart home devices and CCTV support. No FUP. VAT included.',
 'https://cgnet.com.np/wifi-six', '{"wifi_standard":"802.11ax","max_ap_users":128,"deposit_npr":500,"install_charge_npr":3000,"new_connection_only":true,"badge":"best_value"}'),


(5, 'CGNet Wi-Fi 6 400 Mbps Internet Only 12 Months',
 'CGNet WiFi6 400 12M', 'fiber', 'active',
 400, '400 Mbps',
 1208, NULL, 14499, 'Rs. 14,499 / year',
 true, true, 12,
 '[{"type":"router","name":"Huawei OptiXstar HG8145X6 (Wi-Fi 6 ONT)"},{"type":"other","name":"No FUP"},{"type":"other","name":"Smart Home Automation Support"},{"type":"other","name":"Content Creation Workflow Support"}]',
 '{"router"}',
 'CGNet Wi-Fi 6 400 Mbps. Fastest tier. Designed for ~8-12+ active users and power users. 4K/8K streams, gaming, content creation, heavy IoT and smart home automation. No FUP. VAT included.',
 'https://cgnet.com.np/wifi-six', '{"wifi_standard":"802.11ax","max_ap_users":128,"deposit_npr":500,"install_charge_npr":3000,"new_connection_only":true,"badge":"fastest"}');


UPDATE isps SET scraper_config = '{
  "plan_list_url": "https://cgnet.com.np/wifi-six",
  "selectors": {
    "plan_container": "#packages .plan-card",
    "name": "h3",
    "price": ".price",
    "speed": ".speed-label"
  },
  "notes": "Server-rendered HTML. Use httpx + BeautifulSoup. Plans in #packages section. Annual pricing only — no monthly/quarterly variants on page."
}'::jsonb WHERE slug = 'cgnet';



INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 5, p.id, 'plan_added', 'high',
  NULL, NULL, NULL, NULL,
  'CGNet Wi-Fi 6 350 Mbps at Rs 1,167/mo (VAT incl) — WorldLink charges Rs 1,300/mo (VAT excl) for only 300 Mbps. CGNet gives more speed at lower effective cost.',
  '{"download_mbps": 350, "price_monthly": 1167, "vat_included": true, "worldlink_nearest_mbps": 300, "worldlink_nearest_price_excl_vat": 1300, "wifi_standard": "802.11ax", "no_fup": true}',
  NOW()
FROM plans p WHERE p.normalized_name = 'CGNet WiFi6 350 12M' LIMIT 1;

INSERT INTO change_logs (
  isp_id, plan_id, change_type, severity,
  field_name, old_value, new_value, diff_pct,
  summary, details, detected_at
)
SELECT 5, p.id, 'plan_added', 'medium',
  NULL, NULL, NULL, NULL,
  'CGNet Wi-Fi 6 400 Mbps at Rs 1,208/mo — matches Vianet 400 Mbps at Rs 1,300/mo but Rs 92 cheaper per month (both VAT included). Vianet still has 600 Mbps tier; CGNet maxes at 400 Mbps.',
  '{"download_mbps": 400, "price_monthly": 1208, "vat_included": true, "vianet_400_price_monthly": 1300, "diff_npr": -92, "cgnet_max_speed_mbps": 400, "vianet_max_speed_mbps": 600}',
  NOW()
FROM plans p WHERE p.normalized_name = 'CGNet WiFi6 400 12M' LIMIT 1;



SELECT '=== CGNET INSERT COMPLETE ===' AS status;
SELECT i.name AS isp, COUNT(p.id) AS plan_count,
       MIN(p.price_annual)::int AS min_annual_npr,
       MAX(p.price_annual)::int AS max_annual_npr,
       MIN(p.download_mbps) AS min_speed_mbps,
       MAX(p.download_mbps) AS max_speed_mbps
FROM plans p
JOIN isps i ON i.id = p.isp_id
WHERE i.slug = 'cgnet'
GROUP BY i.name;
