INSERT INTO plans (
  id, isp_id, raw_name, normalized_name, plan_type, status,
  download_mbps, speed_raw,
  price_monthly, price_quarterly, price_annual, price_raw,
  vat_included, is_unlimited, contract_months,
  bundles, bundle_flags, description, scrape_url, raw_data
) VALUES

(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet Only 3 Months', 'Subisu 200 IO 3M', 'residential', 'active',
 200, '200 Mbps', 1106.33, 3319, NULL, 'Rs. 3,319 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"router"}',
 'Subisu FTTH 200 Mbps internet only. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet Only 12 Months', 'Subisu 200 IO 12M', 'residential', 'active',
 200, '200 Mbps', 774, NULL, 9292, 'Rs. 9,292 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"router"}',
 'Subisu FTTH 200 Mbps internet only. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet Only 3 Months', 'Subisu 300 IO 3M', 'residential', 'active',
 300, '300 Mbps', 1357, 4071, NULL, 'Rs. 4,071 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"router"}',
 'Subisu FTTH 300 Mbps internet only. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet Only 12 Months', 'Subisu 300 IO 12M', 'residential', 'active',
 300, '300 Mbps', 1069, NULL, 12831, 'Rs. 12,831 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"router"}',
 'Subisu FTTH 300 Mbps internet only. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet + Clear TV 3 Months', 'Subisu 200 TV 3M', 'residential', 'active',
 200, '200 Mbps', 1329.67, 3989, NULL, 'Rs. 3,989 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"iptv","router"}',
 'Subisu FTTH 200 Mbps + Clear TV combo. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 200 Mbps Internet + Clear TV 12 Months', 'Subisu 200 TV 12M', 'residential', 'active',
 200, '200 Mbps', 1224, NULL, 14690, 'Rs. 14,690 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"iptv","router"}',
 'Subisu FTTH 200 Mbps + Clear TV combo. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet + Clear TV 3 Months', 'Subisu 300 TV 3M', 'residential', 'active',
 300, '300 Mbps', 1578.33, 4735, NULL, 'Rs. 4,735 / 3 Months (excl. VAT)',
 false, false, 3,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"iptv","router"}',
 'Subisu FTTH 300 Mbps + Clear TV combo. 3-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}'),

(gen_random_uuid(), 3, 'Subisu 300 Mbps Internet + Clear TV 12 Months', 'Subisu 300 TV 12M', 'residential', 'active',
 300, '300 Mbps', 1527, NULL, 18319, 'Rs. 18,319 / 12 Months (excl. VAT)',
 false, false, 12,
 '[{"type":"iptv","name":"Subisu Clear TV"},{"type":"router","name":"5GHz Dual-Band Router Included"}]', '{"iptv","router"}',
 'Subisu FTTH 300 Mbps + Clear TV combo. 12-month subscription. FUP applies. VAT excluded.',
 'https://subisu.net.np/packages', '{"vat_excl": true}');