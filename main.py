import json
import os
import argparse
from datetime import datetime, timedelta
from urllib import request
import ssl

from settings import *


def download(days: int = 0):
    aux = {}
    noc = []
    gen = []

    now = datetime.now()
    to_date = now
    from_date = to_date - timedelta(days)
    # delta_time = now - timedelta(days, 0)

    while from_date <= to_date:
        date_formatted = from_date.strftime("%Y-%m-%d")
        ssl._create_default_https_context = ssl._create_unverified_context
        response = request.urlopen(URL_JSON.format(date_formatted))
        data = json.loads(response.read())
        status_code = response.getcode()

        if status_code == 200 and "PVPC" in data:

            pvpc = []

            for x in data['PVPC']:
                pvpc.append(
                    {"day": x['Dia'], "hours": x['Hora'], "night_plan": float(x['NOC'].replace(",", ".")) / 1000,
                     "General_plan": float(x['GEN'].replace(",", ".")) / 1000})

                noc.append(float(x['NOC'].replace(",", ".")) / 1000)
                gen.append(float(x['GEN'].replace(",", ".")) / 1000)

                aux["PVPC"] = pvpc

                aux["Stats"] = {"min_night": min(noc), "max_night": max(noc), "avg_night": sum(noc) / len(noc),
                                "min_general": min(gen), "max_general": max(gen),
                                "avg_general": sum(gen) / len(gen)}

            write_json(aux, f'{DATA_FOLDER}/{date_formatted}.json')
        elif status_code != 200:
            print('El recurso presenta errores')
            return ()
        else:
            print(f'Ha sido imposible sacar información de la fecha {date_formatted}')
            return ()


        from_date += timedelta(days=1)


def write_json(content: dict, path: str):
    """
    Writes a JSON file
    :param content: JSON content
    :param path: Output path
    """
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(content, file)


def main():
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    parser = argparse.ArgumentParser(description='CRON PROCESS')
    parser.add_argument('-d', '--days', default=0, type=int, help='Downloads data from [today-days, today]')
    args = parser.parse_args()
    days = args.days if args.days >= 0 else 0
    download(days)


if __name__ == '__main__':
    main()
