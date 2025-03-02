import glob
import json
import os
import time
import logging
from datetime import datetime
from random import randint

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def connect_selenium():
    # открываем хром для удаленной отладки через командную строку (порт 9222) - чтобы браузер не сбрасывался между сессиями как в чистом selenium и чтобы избежать детекции запуска через webdriver:
    # /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222

    # подключаемся к открытому хрому
    options = webdriver.ChromeOptions()
    options.add_experimental_option("debuggerAddress", "localhost:9222")
    driver = webdriver.Chrome(options=options)

    # работаем с последним окном, где вручную открыт сайт и произведена авторизация
    windows = driver.window_handles
    driver.switch_to.window(windows[-1])
    return driver

# список хедж фондов, по которым будут собираться данные (все фонды на whalewisdom c большей частью портфеля (70+%) в healthcare)
fund_urls = '''paradigm-biocapital-advisors-lp
sofinnova-ventures-inc
krensavage-asset-management-llc
new-leaf-venture-partners-llc
jw-asset-management-llc
tradelink-capital-llc
rp-management-llc
consonance-capital-management-lp
rtw-investments-llc
sarissa-capital-management-lp
foresite-capital-management-i-llc
opaleye-management-inc
cormorant-asset-management-llc
ghost-tree-capital-llc
vivo-capital-llc
samsara-biocapital-lp
healthcor-management-l-p
sivik-global-healthcare-llc
baker-bros-advisors-llc
sectoral-asset-management-inc
redmile-group-llc
orbimed-advisors-llc
palo-alto-investors-llc
partner-fund-management-l-p-2
oracle-investment-management-inc
dafna-capital-management-llc
bvf-inc-il
cpmg-inc
mpm-asset-management-llc
frazier-management-llc
camber-capital-management-llc
aquilo-capital-management-llc
aisling-capital-management-lp
venbio-select-advisor-llc
stonepine-capital-management-llc
birchview-capital-lp
eversept-partners-llc
zeal-asset-management-ltd
parian-global-management-lp
armistice-capital-llc
boxer-capital-llc
casdin-capital-llc
ecor1-capital-llc
ra-capital-management-llc
vr-adviser-llc'''.split('\n')


def get_portfolios():
    logging.basicConfig(filename="portfolio_scraper.log",
                        format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.INFO)

    driver = connect_selenium()
    logging.info("Connected to Selenium WebDriver")

    # кастомная функция для ожидания загрузки таблицы с потрфелем для обработки случая No data available и других непредвиденных сценариев
    def wait_until_loading_disappears_or_no_data(driver):
        try:
            loading_element = driver.find_element(By.XPATH, "//tr[contains(@class, 'v-data-table__empty-wrapper')]")
            if loading_element.text == "No data available":
                return True
            else:
                return False
        except:
            return True

    # создаем директории
    os.makedirs('data.nosync/ww_reports/raw', exist_ok=True)
    os.makedirs('data.nosync/ww_reports/available_quarters', exist_ok=True)

    for fund_url in fund_urls:
        # идем на страницу фонда
        logging.info(f"Processing fund: {fund_url}")
        driver.get(f"https://whalewisdom.com/filer/{fund_url}")

        # ждем, чтобы все прогрузилось и чтобы скрыть факт автоматизации
        time.sleep(3)

        try:
            # открываем вкладку с потрфолио фонда
            button_holdings = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@role="tab" and normalize-space(text())="Holdings"]')))
            button_holdings.click()
            logging.info(f"Opened Holdings tab for {fund_url}")
        except TimeoutException:
            logging.error(f"Timeout while clicking Holdings button for {fund_url}")
            continue

        # ждем, чтобы все прогрузилось и чтобы скрыть факт автоматизации
        time.sleep(10)

        try:
            # выбираем опцию показывать 100 строк на странице (дефолт - 25)
            # находим dropdown меню
            items_per_page_div = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div[text()='Items per page:']/..")))
            dropdown_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(items_per_page_div.find_element(By.XPATH, ".//div[@role='button']")))
            # открываем dropdown меню
            dropdown_button.click()
            # выбираем опцию показывать 100 строк на странице
            dropdown_menu = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'menuable__content__active')]")))
            option_100 = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(dropdown_menu.find_element(By.XPATH, ".//div[contains(@class, 'v-list-item__title') and text()='100']")))
            option_100.click()
            logging.info(f"Set items per page to 100 for {fund_url}")
        except TimeoutException:
            logging.error(f"Timeout while setting items per page for {fund_url}")
            continue

        # ждем, пока таблица прогрузится
        WebDriverWait(driver, 10).until(wait_until_loading_disappears_or_no_data)

        try:
            # открываем dropdown меню со списком доступных кварталов
            label = WebDriverWait(driver, 5).until(EC.visibility_of_element_located((By.XPATH, "//label[text()='Quarter to view']")))
            parent_div = label.find_element(By.XPATH, "./ancestor::div[contains(@class, 'v-select')]")
            button_dropdown_available_quarters = parent_div.find_element(By.XPATH, ".//div[@role='button']")
            button_dropdown_available_quarters.click()
            # ждем, чтобы все прогрузилось и чтобы скрыть факт автоматизации
            time.sleep(1)
        except TimeoutException:
            logging.error(f"Timeout while opening quarter dropdown for {fund_url}")
            continue

        try:
            # сохраняем список доступных кварталов из dropdown меню для валидации после получения всех данных
            dropdown_menu = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'menuable__content__active')]")))
            available_quarters = dropdown_menu.find_elements(By.XPATH, ".//div[@role='option']//div[@class='v-list-item__title']")
            # не берем кварталы, доступные только по подписке (requires subscription) и текущие данные (current combined) тк они дублируют последний квартал
            available_quarters_list = [option.text for option in available_quarters if option.text.lower() and "requires subscription" not in option.text.lower() and "current combined" not in option.text.lower()]
            json.dump({'quarters': available_quarters_list}, open(f'data.nosync/ww_reports/available_quarters/{fund_url}.json', 'w'))
            logging.info(f"Saved available quarters for {fund_url}")
        except TimeoutException:
            logging.error(f"Timeout while fetching available quarters for {fund_url}")
            continue

        # скачиваем холдинги каждого из доступных кварталов
        for available_quarter_button in available_quarters:
            available_quarter = available_quarter_button.text.lower()
            if available_quarter and "requires subscription" not in available_quarter and "current combined" not in available_quarter:
                try:
                    # выбираем квартал
                    available_quarter_button.click()

                    # ждем, пока таблица прогрузится
                    WebDriverWait(driver, 10).until(wait_until_loading_disappears_or_no_data)

                    # листаем страницы вперед до конца
                    while True:
                        time.sleep(3)
                        next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']")))
                        next_button.click()
                except TimeoutException:
                    # если элемент перехода на следующую страницу не стал кликабельным - собрали все
                    logging.info(f"Collected all pages for quarter {available_quarter} of fund {fund_url}")

                # проверяем, не ограничил ли сайт доступ к последним страницам потрфеля из-за большого количества акций (300+)
                parse_in_reverse = False
                try:
                    element = driver.find_element(By.XPATH, "//*[contains(text(), 'Please log in first to see holdings data')]")
                    logging.info(f"Access restricted to full data, parsing in reverse for {fund_url}")
                    parse_in_reverse = True
                except NoSuchElementException:
                    pass

                # инвертируем сортировку позиций по market value, чтобы сбросить странцу, тк при переходе между кварталами она сохраняется
                # и если в новом квартале будет меньше страниц холдингов, то переход на другие страницы будет недоступен
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//th[.//span[text()='Market Value']]")))
                element.click()

                # и собираем оставшиеся данные - листаем страницы вперед до конца (после изменения сортировки страница сбрасывается на 1)
                if parse_in_reverse:
                    try:
                        while True:
                            time.sleep(3)
                            next_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Next page']")))
                            next_button.click()
                    except TimeoutException:
                        pass

                    # снова инвертируем сортировку позиций по market value, чтобы сбросить странцу, тк при переходе между кварталами она сохраняется
                    # и если в новом квартале будет меньше страниц холдингов, то переход на другие страницы будет недоступен
                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//th[.//span[text()='Market Value']]")))
                    element.click()

                # открываем меню выбора квартала обратно
                button_dropdown_available_quarters.click()
                # ждем, чтобы все прогрузилось и чтобы скрыть факт автоматизации
                time.sleep(3)
                logging.info(f"Processed quarter {available_quarter} for {fund_url}")

# get_portfolios()


# конвертация даты в id квартала whalewisdom - дальнейшая нумерация будет в id
def date_to_quarter_id(date_obj):
    q_year = date_obj.year
    q_month = date_obj.month

    if date_obj.day >= 16:
        q_num = (q_year - 2001) * 4 + (q_month - 2) // 3
    else:
        q_num = (q_year - 2001) * 4 + (q_month - 3) // 3

    return q_num


def parse_portfolios():
    # подгружаем все пути данных по доступным кварталам и потрфолио фондов
    available_quarters_paths = glob.glob('data.nosync/ww_reports/available_quarters/*.json')
    report_paths = glob.glob('data.nosync/ww_reports/raw/*.json')

    # создаем пустые словари для данных
    available_quarters = {}
    data = {}
    available_positions = {}

    # загружаем данные по наличию кварталов для валидации, создаем пустые словари для данных
    for available_quarters_path in available_quarters_paths:
        fund_name = os.path.basename(available_quarters_path)[:-5]
        # + 1 - сдвиг относительно dropdown меню сайта, оно не совпадает со внутренними id кварталов
        available_quarters[fund_name] = [date_to_quarter_id(datetime.strptime(quarter, "%Y-%m-%d").date()) + 1 for quarter in json.load(open(available_quarters_path, 'r'))['quarters']]
        data[fund_name] = {}
        available_positions[fund_name] = {}

    # парсим потрфолио
    for report_path in report_paths:
        # считываем инфо куска таблицы - квартал, фонд, сдвиг, сортировка
        report_info = os.path.basename(report_path)[:-5].split('-')

        # пропускаем отчеты с -1 кварталом - они дублируют последний квартал
        if not report_info[0]:
            continue

        quarter_id = int(report_info[0])
        sorting = report_info[-1]
        offset = report_info[-2]
        # многие фонды пишутся через дефис, возможно, стоило выбрать другой сепаратор, но уже слишком поздно
        fund_name = '-'.join(report_info[1:-2])

        print(quarter_id, sorting, offset, fund_name)

        # добавляем кусок таблицы к остальным данным
        report = json.load(open(report_path, 'r'))
        if quarter_id not in data[fund_name]:
            data[fund_name][quarter_id] = []
        data[fund_name][quarter_id] += report['rows']
        # записываем суммарное количество позиций для финальной валидации, что все страницы таблицы были загружены
        available_positions[fund_name][quarter_id] = report['records']

    # валидация данных
    for fund_name, fund_available_quarters in available_quarters.items():
        for quarter_id in fund_available_quarters:
            # ошибка, если не скачали квартал
            if quarter_id not in data[fund_name]:
                print(fund_name, quarter_id)
                raise

            # ошибка, если не скачали все акции (не все страницы таблицы были загружены)
            data[fund_name][quarter_id] = pd.DataFrame(data[fund_name][quarter_id]).drop_duplicates()
            if len(data[fund_name][quarter_id]) != available_positions[fund_name][quarter_id]:
                print(fund_name, quarter_id)
                raise

            # добавляем метаданные
            data[fund_name][quarter_id]['fund_url'] = fund_name
            data[fund_name][quarter_id]['quarter_id'] = quarter_id

    # собираем все в одну таблицу, выбираем нужные столбцы и сохраняем в паркетник - они эффективнее и быстрее
    df = pd.concat([data[fund_name][quarter_id] for fund_name, fund_available_quarters in available_quarters.items() for quarter_id in fund_available_quarters])[['fund_url', 'quarter_id', 'security_type', 'stock_id', 'current_mv', 'sector', 'permalink', 'name', 'current_shares', 'symbol']]
    df['stock_id'] = df['stock_id'].astype(int)
    df.to_parquet('portfolios.parquet', index=False)
    print('portfolios', df.shape)
    # df.to_excel('portfolios.xlsx', index=False)

parse_portfolios()


def get_stocks():
    logging.basicConfig(filename="stocks_scraper.log",
                        format='%(asctime)s %(levelname)s:%(message)s',
                        level=logging.INFO)

    driver = connect_selenium()
    logging.info("Connected to Selenium WebDriver")

    def search_ticker(stock_name, stock_permalink):
        try:
            # скроллим страницу до окна с поиском (эмуляция пользователя и на случай, если окно поиска уехало из view)
            search_input = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@placeholder="Search for funds/stocks"]')))
            driver.execute_script("arguments[0].scrollIntoView(true);", search_input)

            # ждем, пока окно поиска станет доступным
            clickable_element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@placeholder="Search for funds/stocks"]')))
            logging.info(f"Search input clickable for {stock_name}")

            # закрываем рекламу, если есть
            close_ad()

            # ищем акцию по тикеру (поиск по permalink недоступен)
            clickable_element.click()
            search_input.send_keys(stock_name, Keys.RETURN)
            logging.info(f"Searching for {stock_name}")

            # ждем завершения поиска
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[@class="v-data-table__wrapper"]')))

            try:
                # выбираем ссылку на нужную акцию по уникальному permalink (его уже знаем из отчета фонда)
                specific_link = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, f'//div[@class="v-data-table__wrapper"]//a[@href="/stock/{stock_permalink}"]')))
                # закрываем рекламу, если есть
                close_ad()
                # переходим на страницу акции
                specific_link.click()
                logging.info(f"Navigated to stock page for {stock_name} with permalink {stock_permalink}")
            except TimeoutException:
                logging.error(f"Timeout while searching for specific stock link for {stock_name} with permalink {stock_permalink}")
                # если поиск не удался (в редких случаях) - вручную переходим на страницу акции, но за это может прилететь бан
                driver.get(f"https://whalewisdom.com/stock/{stock_permalink}")
        except Exception as e:
            logging.error(f"Error in search_ticker: {e}")

    # проверяем наличие рекламы на всю страницу и закрываем ее (не дает нажимать кнопки)
    def close_ad():
        try:
            # переключаемся на iframe рекламы через другой iframe рекламы
            WebDriverWait(driver, 2).until(
                EC.frame_to_be_available_and_switch_to_it((By.XPATH, "//iframe[@aria-label='Advertisement' and @width='' and @height='']"))
            )

            WebDriverWait(driver, 2).until(
                EC.frame_to_be_available_and_switch_to_it((By.ID, "ad_iframe"))
            )

            # закрываем рекламу
            close_button = WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close ad']")))
            close_button.click()
            logging.info("Closed advertisement")
        except TimeoutException:
            # рекламы нет
            logging.info("No advertisement to close")
        finally:

            # переключаемся на основной фрейм
            driver.switch_to.default_content()

    # создаем директории
    os.makedirs('data.nosync/stock_info', exist_ok=True)
    os.makedirs('data.nosync/stock_prices', exist_ok=True)
    os.makedirs('data.nosync/stock_pages', exist_ok=True)

    # выбираем нужные акции из всех потрфелей (биотех сектор)
    stocks = pd.read_parquet('portfolios.parquet')
    stocks = stocks[stocks['sector'] == 'HEALTH CARE'][['stock_id', 'permalink', 'name']].drop_duplicates()

    # удаляем уже загруженные акции из списка на загрузку
    stock_ids_exist = [int(os.path.basename(filename)[:-5]) for filename in glob.glob('data.nosync/stock_prices/*.json')]
    new_stocks = stocks[~stocks['stock_id'].isin(stock_ids_exist)]

    total_stocks = len(new_stocks)
    processed = 0
    started = time.time()
    # скачиваем оставшиеся данные
    for stock_id, permalink, name in new_stocks.itertuples(index=False):
        try:
            logging.info(f"Processing stock: {name} ({stock_id}, {permalink})")
            # открываем страницу акции через поиск по тикеру
            search_ticker(name, permalink)
            # ждем, пока график цен прогрузится с учетом того, что его может не быть на странице (очень редко)
            try:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'metric-chart-container')))
            except TimeoutException:
                json.dump({'no chart': 'no chart', 'permalink': permalink}, open(f'data.nosync/stock_prices/{stock_id}.json', 'w'))
                logging.info(f"No chart available for stock: {name} ({stock_id}, {permalink})")
                continue
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'highcharts-root')))
            # рандомная пауза для эмуляции живого пользователя
            time.sleep(randint(2, 5))
        except Exception as e:
            logging.error(f"Error processing stock {name} ({stock_id}): {e}")
        processed += 1
        logging.info(f"Processed {processed}/{total_stocks} ({len(stocks)}), {name} ({stock_id}), {round((time.time()-started)/processed*(total_stocks-processed)/60)} min remains")

# get_stocks()


def parse_stock_prices():
    # парсим данные по ценам
    report_paths = glob.glob('data.nosync/stock_prices/*.json')
    data = []
    for file in report_paths:
        try:
            data.append(pd.read_json(file))
        except:
            # ошибки только для акций без графиков на их страницах
            print(file)
    df = pd.concat(data).rename(columns={'quarter_description': 'date'})
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values(by=['stock_permalink', 'date'], inplace=True)
    df.to_parquet('prices_ww.parquet', index=False)
    print('prices', df.shape)
    # df.to_excel('prices.xlsx', index=False)

parse_stock_prices()


def parse_stock_info():
    # парсим доп. данные по акциям
    stock_info_paths = glob.glob('data.nosync/stock_pages/*.html')
    data = []
    for stock_info_path in stock_info_paths:
        # пропускаем данные формата summary и holdings - нас интересуют только основные параметры
        if 'summary_b_' in stock_info_path or 'holdings.html' in stock_info_path:
            continue

        soup = BeautifulSoup(open(stock_info_path).read(), 'html.parser')

        # ищем название акции, тикер, ссылку на yahoo finance
        company_info = soup.find('h1', class_='text-h4')
        company_name = company_info.get_text(strip=True)
        stock_ticker = company_info.find('a').get_text(strip=True)[1:-1]
        yahoo_finance_link = company_info.find('a')['href']

        # парсим табличку с доп. инфо
        info_table = {}
        rows = soup.select('div.v-data-table__wrapper table tbody tr')
        for row in rows:
            cells = row.find_all('td')
            # ряд должен быть формата key - value
            if len(cells) == 2:
                key = cells[0].get_text(strip=True).rstrip(':')
                value = cells[1].get_text(strip=True)
                info_table[key] = value

        # парсим адрес и номер телефона
        address_block = rows[-1].find('td[colspan="2"] address')
        if address_block:
            address = address_block.contents[0].strip()
            phone = address_block.find('div').get_text(strip=True)
            info_table['Address'] = address
            info_table['Phone'] = phone

        # парсим описание (если есть)
        description = soup.select_one('div.v-card__text div.subtitle-1')
        if description:
            description = description.get_text(strip=True)

        data.append({
            'permalink': os.path.basename(stock_info_path)[:-5],
            'company_name': company_name,
            'stock_ticker': stock_ticker,
            'yahoo_finance_link': yahoo_finance_link,
            'description': description,
        })
        for key, value in info_table.items():
            data[-1][key] = value

    # сохраняем в паркетник
    df = pd.DataFrame(data)
    df.to_parquet('info.parquet')
    print('info', df.shape)
    # df.to_excel('info.xlsx')

parse_stock_info()

