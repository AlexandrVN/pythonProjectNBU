import requests
import json
from datetime import date as d
from datetime import datetime as dt


def main():
    print('Hi')
    headers = {
        "Accept": "*/*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
        Chrome/115.0.0.0 Safari/537.36"
    }

    today = d.today()
    date_end = d(today.year, today.month, today.day)
    # date_start = date_end.replace(year=today.year - 1)

    date_start = date_end.replace(month=today.month - 1)

    start = date_start.strftime("%Y%m%d")
    end = date_end.strftime("%Y%m%d")
    currency = "KRW"
    sort = "exchangedate"  # ('exchangedate' / 'r030' / 'cc' / 'rate')
    order = "desc"  # ('desc' – за спаданням, 'asc' – за зростанням)

    param_start = f'start={start}&'
    param_end = f'end={end}&'
    param_valcode = f'valcode={currency}&'
    param_sort = f'sort={sort}&'
    param_order = f'order={order}&'

    url = f"https://bank.gov.ua/NBU_Exchange/exchange_site?{param_start}{param_end}{param_valcode}{param_sort}{param_order}json"

    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open("result_NBU_data_period.json", "w", encoding="utf-8") as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)

    lst_date = response.json()
    print(type(lst_date))

    # print(lst_date)

    monthly_rate = {'month': [],
                    'rate': []}
    lst_rate = []
    month_pre = ''
    calcdate_pre = ''

    for i in lst_date:
        calcdate = dt.strptime(i['calcdate'], '%d.%m.%Y')
        month = calcdate.month

        if month != month_pre:
            monthly_rate['month'].append(month)
            if len(lst_rate) != 0:
                monthly_rate['rate'].append(lst_rate)
                lst_rate = []

        if calcdate != calcdate_pre:
            lst_rate.append(i['rate_per_unit'])

        month_pre = month
        calcdate_pre = calcdate

    monthly_rate['rate'].append(lst_rate)
    print(monthly_rate)


if __name__ == '__main__':
    main()
