# La Documentation

## Table of Contents
- [La Documentation](#la-documentation)
  - [Table of Contents](#table-of-contents)
  - [Data Sources](#data-sources)
  - [Stock Details (info.parquet)](#stock-details-infoparquet)
    - [Structure](#structure)
    - [Example](#example)
    - [Additional Notes](#additional-notes)
  - [Stock Prices (merged\_prices.parquet)](#stock-prices-merged_pricesparquet)
    - [Structure](#structure-1)
    - [Example](#example-1)
    - [Additional Notes](#additional-notes-1)
  - [Fund Reports (portfolios.parquet)](#fund-reports-portfoliosparquet)
    - [Structure](#structure-2)
    - [Example](#example-2)
    - [Additional Notes](#additional-notes-2)
  - [EDA and Price Fixing](#eda-and-price-fixing)
    - [Identifying Anomalies](#identifying-anomalies)
    - [Addressing Price Data Errors](#addressing-price-data-errors)
    - [Corrections Implemented](#corrections-implemented)
    - [Visual Inspection](#visual-inspection)
  - [Contributing](#contributing)
  - [License](#license)

## Data Sources

The primary source of the data utilized in this project is [WhaleWisdom](https://whalewisdom.com/), which aggregates the 13F filings of institutional investment managers and provides comprehensive, searchable databases of these filings. However, to ensure the accuracy and completeness of the information, the data has been meticulously cross-verified using a multitude of reliable financial information platforms.

These additional sources include:

- [Yahoo Finance](https://finance.yahoo.com/): Offers a wide range of financial data, including stock quotes, portfolio management resources, international market data, message boards and mortgage rates.
- [Simply Wall St](https://simplywall.st/): Known for its infographic-style company reports and investment insights drawn from a broad range of data.
- [Stock Split History](http://stocksplithistory.com/): Specializes in tracking historical stock split data for publicly traded companies, helping investors understand past trends and their potential implications.

It's worth noting that despite the careful cross-verification, the accuracy of the data is ultimately dependent on the integrity of these sources.

## Stock Details (info.parquet)

This file contains an up-to-date dataset of different stocks and their respective detailed characteristics, reflecting the most current information available. 629 rows × 10 columns

### Structure

  - `permalink`: Unique string identifier of the company in WhaleWisdom system.
  - `company_name`: The full name of the company.
  - `stock_ticker`: The stock ticker symbol of the company.
  - `yahoo_finance_link`: A link to the company's Yahoo Finance page.
  - `description`: A short description of the company and its operations.
  - `Sector`: The sector in which the company operates.
  - `Industry`: The specific industry of the company.
  - `CEO`: The current Chief Executive Officer of the company.
  - `Employees`: The number of employees working for the company.
  - `Web site`: A link to the company's own page.

### Example

| permalink | company_name                    | stock_ticker | yahoo_finance_link                 | description                                       | Sector      | Industry             | CEO              | Employees | Web site           |
| --------- | ------------------------------- | ------------ | ---------------------------------- | ------------------------------------------------- | ----------- | -------------------- | ---------------- | --------- | ------------------ |
| cah       | Cardinal Health, Inc(CAH)       | CAH          | https://finance.yahoo.com/q?s=CAH  | Cardinal Health, Inc. operates in two segments... | HEALTH CARE | HEALTH CARE SERVICES | Jason M. Hollar  | 46,500    | cardinalhealth.com |
| allr-3    | Allarity Therapeutics Inc(ALLR) | ALLR         | https://finance.yahoo.com/q?s=ALLR | N/A                                               | HEALTH CARE | PHARMACEUTICALS      | James G. Cullem  | 10        | allarity.com       |
| itrm      | Iterum Therapeutics Plc(ITRM)   | ITRM         | https://finance.yahoo.com/q?s=ITRM | Iterum Therapeutics plc is developing sulopene... | HEALTH CARE | PHARMACEUTICALS      | Corey N. Fishman | 10        | iterumtx.com       |
| eras      | Erasca Inc(ERAS)                | ERAS         | https://finance.yahoo.com/q?s=ERAS | Erasca, Inc., a clinical-stage biopharmaceutic... | HEALTH CARE | PHARMACEUTICALS      | Jonathan E. Lim  | 120       | erasca.com         |

### Additional Notes

- All numerical values are represented as strings.



## Stock Prices (merged_prices.parquet)

This file contains a dataset of different stocks, their respective prices (verified and fixed by hand) and additional details about each stock based on funds' 13F filings. 361565 rows × 16 columns

### Structure

  - `stock_permalink`: Unique string identifier of the company in WhaleWisdom system.
  - `closing_price`: The last recorded price at which the stock traded on a particular date.
  - `stock_id`: Unique identifier for a specific stock in WhaleWisdom system.
  - `avg_short_volume`: The average volume of shares that have been sold short over a specific period. Short selling is when investors sell shares they do not own, betting that the stock price will decline.
  - `put_call_ratio`: The ratio of put options to call options held by funds. A higher ratio indicates more put options (bets that the stock price will fall) relative to call options (bets that the stock price will rise). If the value is `None`, it means that either no put or call options were reported by the funds for the given quarter.
  - `total_volume`: The total number of shares that have been traded during this trading day.
  - `sell_buy_ratio`: The ratio of the number of stocks sold to the number of stocks bought during a specific time period. A ratio above 1 indicates more selling activity compared to buying activity.
  - `date`: Date on which stock price and other data was recorded.
  - `market_cap_13f`: Market capitalization of the stock at the time of the 13F filing, expressed in USD.
  - `total_shares`: The total number of shares of the stock held by funds as reported in their 13F filings for the given quarter.
  - `name`: The full name of the company.
  - `quarter_id`: Unique identifier for a specific quarter of a year as defined by WhaleWisdom's numeration system.
  - `average_ranking`: Average ranking of the stock proprietary to WhaleWisdom, its calculation may take into account factors such as price, volume, and other proprietary factors.
  - `net_buys`: Net amount of shares bought by funds in a given quarter. Positive numbers indicate net buying, while negative numbers indicate net selling.
  - `held_by`: Number of funds that reported holding this stock in their 13F filings for the given quarter.
  - `yf_ticker`: The stock ticker symbol of the company, in case the closing_price data were overwritten with yahoo finance ones.

### Example

| stock_permalink | closing_price | stock_id | avg_short_volume | put_call_ratio | total_volume | sell_buy_ratio | date       | market_cap_13f | total_shares | name                          | quarter_id | average_ranking | net_buys | held_by | yf_ticker |
| --------------- | ------------- | -------- | ---------------- | -------------- | ------------ | -------------- | ---------- | -------------- | ------------ | ----------------------------- | ---------- | --------------- | -------- | ------- | --------- |
| aavl            | 10.00         | 173039   | 111110.0         | 0.009147       | 55649.0      | NaN            | 2022-10-03 | 33238852.0     | 5730320      | AVALANCHE BIOTECHNOLOGIES INC | 88         | 2942.0          | -22.0    | 59      | None      |
| aavl            | 10.30         | 173039   | 34338.0          | 0.009147       | 19911.0      | NaN            | 2022-10-04 | 33238852.0     | 5730320      | AVALANCHE BIOTECHNOLOGIES INC | 88         | 2942.0          | -22.0    | 59      | None      |
| aavl            | 10.10         | 173039   | 40076.0          | 0.009147       | 17821.0      | NaN            | 2022-10-05 | 33238852.0     | 5730320      | AVALANCHE BIOTECHNOLOGIES INC | 88         | 2942.0          | -22.0    | 59      | None      |
| aavl            | 10.20         | 173039   | 61479.0          | 0.009147       | 22047.0      | NaN            | 2022-10-06 | 33238852.0     | 5730320      | AVALANCHE BIOTECHNOLOGIES INC | 88         | 2942.0          | -22.0    | 59      | None      |

### Additional Notes

- Certain features are based on 13F filings, which are quarterly reports filed by institutional investment managers with at least $100 million in equity assets under management. They change once every quarter.



## Fund Reports (portfolios.parquet)

A comprehensive dataset detailing various stocks within different funds' portfolios, encompassing essential characteristics and financial metrics based on funds' 13F filings. 21116 rows × 10 columns (не чистили, тк датасет использовался исключительно для получения списка биотех-акций whalewisdom)

### Structure

  - `fund_url`:
  - `quarter_id`: Unique identifier for a specific quarter of a year as defined by WhaleWisdom's numeration system.
  - `security_type`: Type of equity (e.g., `SH`, `CALL`, `PRN`, `PUT`).
  - `stock_id`: Unique identifier for a specific stock in WhaleWisdom system.
  - `current_mv`: The current market value of the stock in the fund's portfolio.
  - `sector`: The sector in which the company operates.
  - `permalink`: Unique string identifier of the company in WhaleWisdom system.
  - `name`: The full name of the company.
  - `current_shares`: The current shares held value of the stock in the fund's portfolio.
  - `symbol`: The stock ticker symbol of the company.

### Example

| fund_url                        | quarter_id | security_type | stock_id | current_mv | sector      | permalink | name                     | current_shares | symbol |
| ------------------------------- | ---------- | ------------- | -------- | ---------- | ----------- | --------- | ------------------------ | -------------- | ------ |
| krensavage-asset-management-llc | 96         | SH            | 3372     | 32481000   | HEALTH CARE | uthr      | United Therapeutics Corp | 92057.00       | UTHR   |
| krensavage-asset-management-llc | 96         | SH            | 5525     | 32163000   | HEALTH CARE | exel      | Exelixis Inc             | 965866.00      | EXEL   |
| krensavage-asset-management-llc | 96         | SH            | 292      | 24700000   | HEALTH CARE | cah       | Cardinal Health, Inc     | 208845.00      | CAH    |
| krensavage-asset-management-llc | 96         | SH            | 4853     | 16657000   | HEALTH CARE | biib      | Biogen Inc               | 108923.00      | BIIB   |
| krensavage-asset-management-llc | 96         | SH            | 3621     | 13030000   | HEALTH CARE | jazz      | Jazz Pharmaceuticals plc | 105803.00      | JAZZ   |


### Additional Notes

- The equity types 'CALL', 'PUT', and 'PRN' refer to different types of securities. 'CALL' refers to call options, 'PUT' refers to put options, and 'PRN' refers to principal amounts of bonds or other debt securities.



## EDA and Price Fixing

During the exploratory data analysis (EDA) and further data cleansing steps, several anomalies and issues with the stock price data were identified and rectified.

### Identifying Anomalies
An initial step in the data cleansing process involved identifying and removing values of `0` and `NaN` from the price data. This step led to the removal of 8,321 values, accounting for 2.25% of the dataset.

Further scrutiny was applied to identify records requiring additional verification. This included stocks with:
- A `date_diff` greater than 5
- A `price_change_perc` less than -60%
- A `price_change_perc` greater than 180%

This process highlighted 393 values needing further verification for 133 different stocks. These values were cross-referenced and corrected using a secondary data source.

### Addressing Price Data Errors

Several discrepancies in the closing prices from WhaleWisdom were observed for the following stocks: MTEM, VTAK, APTO, LPTX, GENE, KRRO, QTTB, DRMA, CRBP, CKPT, BNTC, AWH, QNRX, and TOVX. These discrepancies were mainly due to reverse stock splits, which were not initially accounted for.

### Corrections Implemented
For the majority of the stocks, the price data from Yahoo Finance was accurate. However, for a few stocks, manual adjustments were necessary. In two cases, data from WhaleWisdom was corrected directly as Yahoo Finance did not retain data for delisted stocks or had errors as well:

- **APRE**: A reverse split on 13.02.2023 (1 for 20)
- **TECX**: A reverse split on 21.06.2024 (1 for 12)
- **MBRX**: A reverse split on 22.03.2024 (1 for 15)
- **MGTA**: A reverse split on 09.11.2023 (1 for 16)
- **PRFX**: A reverse split on 21.11.2024 (1 for 4)

For these stocks, both pre-correction and post-correction price trends were visualized to ensure accuracy.

This meticulous process ensured the reliability and consistency of the stock price data, forming a robust foundation for subsequent analysis and modeling tasks in this project.

### Visual Inspection

For each stock where a manual fix was applied, visual inspection plots were created using Plotly to compare pre-fix and post-fix price trends. This step ensured that our corrections aligned with historical price performance and provided an additional layer of validation.



## Contributing

If you find any issues with the stock data or have suggestions for improvement, please feel free to contribute.



## License

This Git repository has been prepared by team_11 for GP2, featuring historical data of stocks and hedge funds. While the data in this repository has been collated with genuine care and good faith, it is provided solely for informational purposes and should not be taken as financial advice. No representation or warranty, express or implied, is made regarding the accuracy, completeness, or reliability of any data, estimates, opinions or other information contained in this repository.

This repository may contain forward-looking projections. These are based upon team_11's expectations and beliefs concerning future developments and their potential impact, and are subject to risks and uncertainties which, in many cases, are beyond the control of team_11. No assurance is given that future developments will align with end users' expectations. The actual outcomes could differ significantly from those anticipated.

To the maximum extent permitted by law, neither team_11 nor their directors, officers, or employees accept any liability for any loss or damage incurred as a result of reliance upon this information. This repository does not constitute an offer to sell, buy or solicit any security, financial product or service. Any such offer or solicitation should be made only pursuant to an appropriate Disclosure Statement, Information Memorandum, Prospectus, or other offer document relating to a financial product or service.

Past performance is not necessarily indicative of future results and no entity guarantees the performance of any financial product or service, or the amount or timing of any return from it. There can be no assurance that any financial product or service will achieve any targeted return, that asset allocations will be met, or that the financial product or service will be able to implement its investment strategy and investment approach, or achieve its investment objective.

The information contained in this repository is not intended to be relied upon as advice to investors or potential investors, who should consider seeking independent professional advice depending on their specific investment objectives, financial situation, or particular needs.
