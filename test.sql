 SELECT m.symbol,
           m.tr_date,
           m.close,
           u.crossing AS uc,
           d.crossing AS dc
    FROM stock_prices m
    LEFT JOIN (
        SELECT symbol,
               tr_date,
               close,
               crossing
        FROM stock_prices
        WHERE crossing IN ('[U]p')
    ) u ON m.symbol = u.symbol
    AND m.tr_date = u.tr_date
    LEFT JOIN (
        SELECT symbol,
               tr_date,
               close,
               crossing
        FROM stock_prices
        WHERE crossing IN ('[D]own')
    ) d ON m.symbol = d.symbol
    AND m.tr_date = d.tr_date

;    
select *
from (
        SELECT CASE
                WHEN ROW_NUMBER() OVER (
                    PARTITION BY m.symbol
                    ORDER BY m.tr_date
                ) = 1 THEN m.symbol
                ELSE ''
            END AS symbol,
            m.tr_date,
            m.close,
            ifnull(u.crossing, '') AS uc,
            ifnull(d.crossing, '') AS dc
        FROM stock_prices m
            LEFT JOIN (
                SELECT symbol,
                    tr_date,
                    close,
                    crossing
                FROM stock_prices
                WHERE crossing IN ('[U]p')
            ) u ON m.symbol = u.symbol
            AND m.tr_date = u.tr_date
            LEFT JOIN (
                SELECT symbol,
                    tr_date,
                    close,
                    crossing
                FROM stock_prices
                WHERE crossing IN ('[D]own')
            ) d ON m.symbol = d.symbol
            AND m.tr_date = d.tr_date
    )
where symbol <> ''
    or uc <> ''
    or dc <> ''