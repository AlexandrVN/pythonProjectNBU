import json
import csv

import requests
import locale
import datetime as dtd

def main():
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/115.0.0.0 Safari/537.36"
    }

    # Вказуємо українську локаль
    locale.setlocale(locale.LC_TIME, 'uk_UA')  # в інших випадках може бути 'uk_UA.utf8'

    # Отримуємо поточну дату
    today = dtd.date.today()
    # today = dtd.date.fromisoformat('2023-07-04') # змінна для тестування

    # період відбору 1 рік (відбір повних 12 місяців від поточної дати)
    date_start = today.replace(year=today.year - 1, day=1)
    date_end = today.replace(day=1) - dtd.timedelta(days=1)

    # Присвоєння значень параметрам запиту
    start = date_start.strftime("%Y%m%d")
    end = date_end.strftime("%Y%m%d")
    currency = "EUR"
    sort = "exchangedate"  # ('exchangedate' / 'r030' / 'cc' / 'rate')
    order = "asc"  # ('desc' – за спаданням, 'asc' – за зростанням)

    url = f"https://bank.gov.ua/NBU_Exchange/exchange_site?start={start}&end={end}&valcode={currency}&sort={sort}&order={order}&json"

    s = requests.Session()
    response = s.get(url=url, headers=headers)

    # # Збереження отриманного результату в файл формату JSON
    # with open(f"result_NBU_data_period-{currency}.json", "w", encoding="utf-8") as file:
    #     json.dump(response.json(), file, indent=4, ensure_ascii=False)

    # # Збереження отриманного результату в файл формату CSV
    # with open(f"result_NBU_data_period-{currency}.csv", "w", newline='', encoding="utf-8") as file:
    #     spamwriter = csv.writer(file, delimiter=' ', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    #     # spamwriter.writerow([''] + [''] + [''] + [''] + [''])
    #     # spamwriter.writerow(['', '', '', '', ''])

    # Збереження отриманного результату до змінної
    lst_date_period = response.json()

    monthly_rate = {'month': [],
                    'rate': []}
    lst_rate = []
    month_pre = ''
    calcdate_pre = ''

    '''
    Параметр date_rate може набувати значень 'exchangedate' та 'calcdate':
        - по календарним дням - використовується дата з поля 'exchangedate', для розрахунку середнього значення курсу, 
        при цьому береться курс за кожен день місяця (по цій методиці визначається середній курс на сайті НБУ);
        - по робочим дням - використовується дата з поля 'calcdate', для розрахунку середнього значення курсу,  
        при цьому береться курс тільки за дні місяця, в які він встановлювався;
    '''
    date_rate = 'exchangedate'

    for i in lst_date_period:
        calcdate = dtd.datetime.strptime(i[date_rate], '%d.%m.%Y')
        month = calcdate.strftime('%Y_%B')

        if calcdate.date() < date_start:
            continue
        else:
            if month != month_pre:
                monthly_rate['month'].append(month)
                if len(lst_rate) != 0:
                    monthly_rate['rate'].append(lst_rate)
                    lst_rate = []

            if calcdate != calcdate_pre:
                lst_rate.append(i['rate_per_unit'])

            month_pre = month
            calcdate_pre = calcdate

    # Перевірка на пустий список
    if len(lst_rate) == 0:
        monthly_rate['month'].pop()
    else:
        monthly_rate['rate'].append(lst_rate)

    # print(monthly_rate)

# Визначення середнього значення та відхилення курсу за кожний місяць

    count_of_months = len(monthly_rate['month'])
    monthly_rate.update({'average': [], 'deviation': []})

    for k in range(count_of_months):
        average_curr = float(sum(monthly_rate['rate'][k]) / len(monthly_rate['rate'][k]))

        if (k - 1) < 0:
            average_prev = average_curr
        else:
            average_prev = float(sum(monthly_rate['rate'][k - 1]) / len(monthly_rate['rate'][k - 1]))

            # З округленням
        average = '%.4F' % (average_curr)
        deviation = '%.4F' % (average_curr - average_prev)
        monthly_rate['average'].append(average)
        monthly_rate['deviation'].append(deviation)

        #     # Без округлення
        #     monthly_rate['average'].append(average_curr)
        #     monthly_rate['deviation'].append(average_curr - average_prev)

        print(f"Період: {monthly_rate['month'][k]}")
        print(f"Середне значення курсу по валюті {currency}: {average}")
        print(f"Відхилення: {deviation}")
        print()
        print()

    # print(monthly_rate)


if __name__ == '__main__':
    main()
