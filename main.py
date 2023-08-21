import requests
import json
import locale
from datetime import date as d
from datetime import datetime as dt


def main():
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/115.0.0.0 Safari/537.36"
    }

    # Вказуємо українську локаль
    locale.setlocale(locale.LC_TIME, 'uk_UA')  # в інших випадках може бути 'uk_UA.utf8'

    today = d.today()
    date_end = d(today.year, today.month, today.day)
    date_start = date_end.replace(year=today.year - 1)  # період відбору з кроком 1 рік від поточної дати
    # date_start = date_end.replace(month=today.month - 1)      # період відбору з кроком 1 місяць від поточної дати

    start = date_start.strftime("%Y%m%d")
    end = date_end.strftime("%Y%m%d")
    currency = "EUR"
    sort = "exchangedate"  # ('exchangedate' / 'r030' / 'cc' / 'rate')
    order = "desc"  # ('desc' – за спаданням, 'asc' – за зростанням)

    url = f"https://bank.gov.ua/NBU_Exchange/exchange_site?start={start}&end={end}&valcode={currency}&sort={sort}&order={order}&json"

    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open(f"result_NBU_data_period-{currency}.json", "w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)

    lst_date_period = response.json()

    # print(type(lst_date_period))
    # print(lst_date_period)

    monthly_rate = {'month': [],
                    'rate': []}
    lst_rate = []
    month_pre = ''
    calcdate_pre = ''

    for i in lst_date_period:
        '''
        По календарним дням - при використанні дати з поля 'exchangedate', для розрахунку середнього значення курсу
        беремо курс за кожен день. По цій методиці визначається середній курс на сайті НБУ

        По робочим дням - при використанні дати з поля 'calcdate', для розрахунку середнього значення курсу 
        беремо курс тільки за дні, в які він встановлювався
        '''
        # calcdate = dt.strptime(i['exchangedate'], '%d.%m.%Y')
        calcdate = dt.strptime(i['calcdate'], '%d.%m.%Y')

        month = calcdate.strftime('%Y_%B')

        if month != month_pre:
            monthly_rate['month'].append(month)
            if len(lst_rate) != 0:
                monthly_rate['rate'].append(lst_rate)
                lst_rate = []

        if calcdate != calcdate_pre:
            lst_rate.append(i['rate_per_unit'])

        month_pre = month
        calcdate_pre = calcdate

    # можемо отримати пустий список, якщо кінець відбору припаде на вихідні на початку нового місяця
    # перед записом останнього списку перевіряємо його на заповненність, якщо пусто то видаляємо останній записаний елемент 'month'
    if len(lst_rate) == 0:
        monthly_rate['month'].pop()
    else:
        monthly_rate['rate'].append(lst_rate)

    # print(monthly_rate)

# Вивести середнє значення та відхилення курсу за кожний місяць.
# Дану інформацію записати у файл за допомогою pickle.

    average_prev = 0
    arrey_rate = len(monthly_rate['month'])
    for k in range(arrey_rate):
        average_curr = float(sum(monthly_rate['rate'][k]) / len(monthly_rate['rate'][k]))
        if (k + 1) < arrey_rate:
            average_prev = float(sum(monthly_rate['rate'][k + 1]) / len(monthly_rate['rate'][k + 1]))

        average = '%.4F' % (average_curr)
        deviation = '%.4F' % (average_curr - average_prev)

        print(f"Період: {monthly_rate['month'][k]}")
        print(f"Середне значення курсу по валюті {currency}: {average}")
        print(f"Відхилення: {deviation}")
        print()

        print()
        print()


if __name__ == '__main__':
    main()
