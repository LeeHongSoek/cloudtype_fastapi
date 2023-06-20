UPDATE sp500_stocks set able = '' ;

UPDATE sp500_stocks set able = 'Y' ;

























SELECT CASE WHEN ROW_NUMBER() OVER (
                        PARTITION BY symbol
                        ORDER BY up_tr_date
                 ) = 1 THEN symbol
          ELSE ''
     END AS symbol
	   , max(up_tr_date) up_tr_date
	   , max(down_tr_date) down_tr_date
	   , max(up_close) up_close
	   , max(down_close) down_close
	   , max(down_close) - max(up_close) diff
from 
(	 
	SELECT CAST(round((ROW_NUMBER() OVER (ORDER BY a.symbol) * 0.5)+0.1) as int) AS record_number
	   , a.symbol
	   ,CASE WHEN a.uc = '[U]p' THEN a.tr_date END up_tr_date
	   ,CASE WHEN a.dc = '[D]own' THEN a.tr_date END  down_tr_date
	   ,CASE WHEN a.uc = '[U]p' THEN a.close END up_close
	   ,CASE WHEN a.dc = '[D]own' THEN a.close END  down_close

	FROM (
		SELECT m.symbol
			 , m.tr_date
			 , m.close
			 , IFNULL(u.crossing, '') AS uc
			 , IFNULL(d.crossing, '') AS dc
		FROM stock_prices m
		LEFT JOIN (
					SELECT symbol
						 , tr_date
						 , close
						 , crossing
					  FROM stock_prices
					 WHERE crossing IN ('[U]p')
				  ) u 
			   ON m.symbol = u.symbol
			  AND m.tr_date = u.tr_date
		LEFT JOIN (
					SELECT symbol
						 , tr_date
						 , close
						 , crossing
					  FROM stock_prices
					 WHERE crossing IN ('[D]own')
				  ) d 
			   ON m.symbol = d.symbol
			  AND m.tr_date = d.tr_date
		WHERE m.tr_date >= '2022-01-01'
		  AND NOT (uc = '' AND dc = '')
	) a
	INNER JOIN (
					SELECT symbol
						 , MIN(tr_date) AS tr_date
					  FROM stock_prices
					 WHERE crossing IN ('[D]own')
					   AND tr_date >= '2022-01-01'
					 GROUP BY symbol
				) n 
		ON a.symbol = n.symbol
	   AND a.tr_date > n.tr_date
	INNER JOIN (
					SELECT symbol
						 , MAX(tr_date) AS tr_date
					  FROM stock_prices
					 WHERE crossing IN ('[U]p')
					   AND tr_date >= '2022-01-01'
					 GROUP BY symbol
				) x 
		ON a.symbol = x.symbol
	   AND a.tr_date < x.tr_date
)	   
group by record_number, symbol
