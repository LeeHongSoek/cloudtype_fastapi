SELECT *
FROM
(
SELECT m.symbol, m.tr_date, m.close , u.crossing uc, d.crossing dc
  from stock_prices m
left join   
(
SELECT symbol, tr_date, close, crossing from stock_prices
where crossing in ('[U]p')
) u
on m.symbol = u.symbol 
and m.tr_date = u.tr_date
left join   
(
SELECT symbol, tr_date, close, crossing from stock_prices
where crossing in ('[D]own')
) d
on m.symbol = d.symbol 
and m.tr_date = d.tr_date
)
where uc is not null or  dc is not null 
ORDER by 1,2
