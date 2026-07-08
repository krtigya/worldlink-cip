
--REAL DATA — Subisu Cablenet (isp_id = 3)
-- Source: nepalitelecom.com (updated May 6, 2026)
-- ALL prices EXCLUDE 13% VAT (Subisu pricing policy)
-- VAT-inclusive price = price * 1.13
-- Plans: Internet Only, Internet + Clear TV
-- Durations: 3 Months, 12 Months
-- FUP: Yes (speed reduced 80-90% after threshold, threshold not published)


DELETE FROM plans WHERE isp_id = 3;

INSERT INTO plans (
    id, isp_id, name, short_name, plan_type, status,
    download_mbps, download_display, price_monthly, price_setup, price_annual,
    price_display, is_promotional, is_bundled, contract_months,
    addons, addon_tags, description, source_url, metadata
) VALUES
(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet Only 3 Months', 'Subisu 200 IO 3M', 'residential', 'active', 200, '200 Mbps', 3319, NULL, NULL, 'Rs. 3,319 / 3M excl VAT', false, false, 3, '[{"type":"router","name":"5GHz Router"}]', '{router}', 'Subisu 200 Mbps internet only. 3-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet Only 12 Months', 'Subisu 200 IO 12M', 'residential', 'active', 200, '200 Mbps', 774, NULL, 9292, 'Rs. 9,292 / 12M excl VAT', false, false, 12, '[{"type":"router","name":"5GHz Router"}]', '{router}', 'Subisu 200 Mbps internet only. 12-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet Only 3 Months', 'Subisu 300 IO 3M', 'residential', 'active', 300, '300 Mbps', 4071, NULL, NULL, 'Rs. 4,071 / 3M excl VAT', false, false, 3, '[{"type":"router","name":"5GHz Router"}]', '{router}', 'Subisu 300 Mbps internet only. 3-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet Only 12 Months', 'Subisu 300 IO 12M', 'residential', 'active', 300, '300 Mbps', 1069, NULL, 12831, 'Rs. 12,831 / 12M excl VAT', false, false, 12, '[{"type":"router","name":"5GHz Router"}]', '{router}', 'Subisu 300 Mbps internet only. 12-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 200 Mbps + Clear TV 3 Months', 'Subisu 200 TV 3M', 'residential', 'active', 200, '200 Mbps', 3989, NULL, NULL, 'Rs. 3,989 / 3M excl VAT', false, false, 3, '[{"type":"iptv","name":"Clear TV"},{"type":"router","name":"5GHz Router"}]', '{iptv,router}', 'Subisu 200 Mbps + Clear TV. 3-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 200 Mbps + Clear TV 12 Months', 'Subisu 200 TV 12M', 'residential', 'active', 200, '200 Mbps', 1224, NULL, 14690, 'Rs. 14,690 / 12M excl VAT', false, false, 12, '[{"type":"iptv","name":"Clear TV"},{"type":"router","name":"5GHz Router"}]', '{iptv,router}', 'Subisu 200 Mbps + Clear TV. 12-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 300 Mbps + Clear TV 3 Months', 'Subisu 300 TV 3M', 'residential', 'active', 300, '300 Mbps', 4735, NULL, NULL, 'Rs. 4,735 / 3M excl VAT', false, false, 3, '[{"type":"iptv","name":"Clear TV"},{"type":"router","name":"5GHz Router"}]', '{iptv,router}', 'Subisu 300 Mbps + Clear TV. 3-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}'),
(gen_random_uuid(), 3, 'Subisu 300 Mbps + Clear TV 12 Months', 'Subisu 300 TV 12M', 'residential', 'active', 300, '300 Mbps', 1527, NULL, 18319, 'Rs. 18,319 / 12M excl VAT', false, false, 12, '[{"type":"iptv","name":"Clear TV"},{"type":"router","name":"5GHz Router"}]', '{iptv,router}', 'Subisu 300 Mbps + Clear TV. 12-month. FUP applies. VAT excluded.', 'https://subisu.net.np/packages', '{"vat_excl":true}');


-- 200 Mbps Internet Only — 3 Months
(3, 'Subisu 200 Mbps Internet Only 3 Months',
 'Subisu 200 IO 3M', 'residential', 'active',
 200, '200 Mbps',
 3319, NULL, NULL, 'Rs. 3,319 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"router"}',
 'Subisu FTTH 200 Mbps internet only. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"installation_router_activation":2035,"installation_wire":752,"installation_charge":"free","vat_excl":true}'),

-- 200 Mbps Internet Only — 12 Months
(3, 'Subisu 200 Mbps Internet Only 12 Months',
 'Subisu 200 IO 12M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, 9292, 'Rs. 9,292 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"router"}',
 'Subisu FTTH 200 Mbps internet only. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"installation_router_activation":1504,"installation_wire":708,"installation_charge":"free","vat_excl":true}'),

-- 300 Mbps Internet Only — 3 Months
(3, 'Subisu 300 Mbps Internet Only 3 Months',
 'Subisu 300 IO 3M', 'residential', 'active',
 300, '300 Mbps',
 4071, NULL, NULL, 'Rs. 4,071 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"router"}',
 'Subisu FTTH 300 Mbps internet only. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"installation_router_activation":2035,"installation_wire":752,"installation_charge":"free","vat_excl":true}'),

-- 300 Mbps Internet Only — 12 Months
(3, 'Subisu 300 Mbps Internet Only 12 Months',
 'Subisu 300 IO 12M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, 12831, 'Rs. 12,831 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"router"}',
 'Subisu FTTH 300 Mbps internet only. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"installation_router_activation":1504,"installation_wire":708,"installation_charge":"free","vat_excl":true}'),




-- 200 Mbps + Clear TV — 3 Months
(3, 'Subisu 200 Mbps Internet + Clear TV 3 Months',
 'Subisu 200 TV 3M', 'residential', 'active',
 200, '200 Mbps',
 3989, NULL, NULL, 'Rs. 3,989 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"iptv","router"}',
 'Subisu FTTH 200 Mbps + Clear TV combo. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"clear_tv_charge_3m":664,"stb_activation":2522,"vat_excl":true}'),

-- 200 Mbps + Clear TV — 12 Months
(3, 'Subisu 200 Mbps Internet + Clear TV 12 Months',
 'Subisu 200 TV 12M', 'residential', 'active',
 200, '200 Mbps',
 NULL, NULL, 14690, 'Rs. 14,690 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"iptv","router"}',
 'Subisu FTTH 200 Mbps + Clear TV combo. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"clear_tv_charge_12m":2655,"stb_activation":2035,"vat_excl":true}'),

-- 300 Mbps + Clear TV — 3 Months
(3, 'Subisu 300 Mbps Internet + Clear TV 3 Months',
 'Subisu 300 TV 3M', 'residential', 'active',
 300, '300 Mbps',
 4735, NULL, NULL, 'Rs. 4,735 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"iptv","router"}',
 'Subisu FTTH 300 Mbps + Clear TV combo. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"clear_tv_charge_3m":664,"stb_activation":2522,"vat_excl":true}'),

-- 300 Mbps + Clear TV — 12 Months
(3, 'Subisu 300 Mbps Internet + Clear TV 12 Months',
 'Subisu 300 TV 12M', 'residential', 'active',
 300, '300 Mbps',
 NULL, NULL, 18319, 'Rs. 18,319 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]',
 '{"iptv","router"}',
 'Subisu FTTH 300 Mbps + Clear TV combo. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages',
 '{"clear_tv_charge_12m":2655,"stb_activation":2035,"vat_excl":true}');



UPDATE isps SET scraper_config = '{
  "plan_list_url": "https://subisu.net.np/packages",
  "render_type": "spa",
  "notes": "JavaScript-required SPA. Use Playwright. Prices are VAT EXCLUSIVE — multiply by 1.13 for VAT-inclusive comparison with other ISPs.",
  "selectors": {
    "plan_container": ".package-card",
    "speed": ".speed",
    "price": ".price"
  }
}'::jsonb WHERE slug = 'subisu';




-- Subisu 300 Mbps vs WorldLink 300 Mbps (VAT-adjusted comparison)
-- Subisu: Rs 4,071 excl VAT = Rs 4,600 incl VAT
-- WorldLink: Rs 4,050 incl VAT
-- WorldLink is cheaper by ~12% VAT-adjusted
INSERT INTO change_logs (
    isp_id, plan_id, change_type, severity,
    field_name, old_value, new_value, diff_pct,
    summary, details, detected_at
)
SELECT 3, p.id, 'plan_added', 'high',
    NULL, NULL, NULL, NULL,
    'Subisu 300 Mbps at Rs 4,071/3M (excl VAT = ~Rs 4,600 incl VAT). WorldLink 300 Mbps at Rs 4,050 incl VAT — WorldLink is ~12% cheaper on VAT-adjusted basis.',
    '{"download_mbps":300,"subisu_price_excl_vat":4071,"subisu_price_incl_vat_est":4600,"worldlink_price_incl_vat":4050,"worldlink_cheaper_pct":12,"note":"Subisu prices are VAT exclusive, all others VAT inclusive"}',
    NOW()
FROM plans p WHERE p.normalized_name = 'Subisu 300 IO 3M' LIMIT 1;



SELECT '=== SUBISU INSERT COMPLETE ===' AS status;
SELECT i.name AS isp, COUNT(p.id) AS plan_count,
       MIN(p.price_monthly) AS min_price,
       MAX(COALESCE(p.price_annual, p.price_monthly)) AS max_price
FROM plans p
JOIN isps i ON i.id = p.isp_id
WHERE i.slug = 'subisu'
GROUP BY i.name;