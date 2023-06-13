-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3306
-- 생성 시간: 23-06-13 21:44
-- 서버 버전: 10.5.21-MariaDB-1:10.5.21+maria~ubu2004
-- PHP 버전: 8.1.20

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- 데이터베이스: `lhs_stock`
--

-- --------------------------------------------------------

--
-- 테이블 구조 `sp500_stocks`
--

CREATE TABLE `sp500_stocks` (
  `symbol` varchar(10) NOT NULL,
  `company_name` varchar(255) NOT NULL,
  `date_update` datetime NOT NULL,
  `date_create` datetime NOT NULL,
  `able` enum('Y','n') NOT NULL DEFAULT 'Y',
  `favorite` enum('Y','n') DEFAULT 'n'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- 테이블 구조 `stock_prices`
--

CREATE TABLE `stock_prices` (
  `symbol` varchar(10) NOT NULL,
  `tr_date` date NOT NULL,
  `open` decimal(10,2) DEFAULT NULL,
  `close` decimal(10,2) DEFAULT NULL,
  `change_rate` decimal(5,2) DEFAULT NULL,
  `volume` int(11) DEFAULT NULL,
  `avg_5` decimal(10,2) DEFAULT NULL,
  `avg_20` decimal(10,2) DEFAULT NULL,
  `date_update` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- 트리거 `stock_prices`
--
DELIMITER $$
CREATE TRIGGER `set_date_update_value` BEFORE INSERT ON `stock_prices` FOR EACH ROW BEGIN
    SET NEW.date_update = NOW();
    
    IF (
        SELECT COUNT(*) + 1
        FROM stock_prices
        WHERE symbol = NEW.symbol
          AND tr_date < NEW.tr_date
        ORDER BY tr_date DESC
        LIMIT 4
    ) < 5 THEN
        SET NEW.avg_5 = NULL;
    ELSE
        SET NEW.avg_5 = (
            (
                SELECT IFNULL(SUM(`close`), 0)
                FROM (
                      SELECT *
                        FROM stock_prices
                        WHERE symbol = NEW.symbol
                          AND tr_date < NEW.tr_date
                     ORDER BY tr_date DESC
                        LIMIT 4
                    ) a
            ) + NEW.close
        ) / 5;
    END IF;
    
    IF (
        SELECT COUNT(*) + 1
        FROM stock_prices
        WHERE symbol = NEW.symbol
          AND tr_date < NEW.tr_date
        ORDER BY tr_date DESC
        LIMIT 19
    ) < 20 THEN
        SET NEW.avg_20 = NULL;
    ELSE
        SET NEW.avg_20 = (
            (
                SELECT IFNULL(SUM(`close`), 0)
                FROM (
                      SELECT *
                        FROM stock_prices
                        WHERE symbol = NEW.symbol
                          AND tr_date < NEW.tr_date
                     ORDER BY tr_date DESC
                        LIMIT 19
                    ) a
            ) + NEW.close
        ) / 20;
    END IF;
END
$$
DELIMITER ;

--
-- 덤프된 테이블의 인덱스
--

--
-- 테이블의 인덱스 `sp500_stocks`
--
ALTER TABLE `sp500_stocks`
  ADD PRIMARY KEY (`symbol`);

--
-- 테이블의 인덱스 `stock_prices`
--
ALTER TABLE `stock_prices`
  ADD PRIMARY KEY (`symbol`,`tr_date`);
COMMIT;
