import pandas as pd
import re
import datetime as dt
from datetime import datetime,timedelta
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from open_sky import OpenSkyApi
from login import username, password
import csv
from ICAO import ICAO

api = OpenSkyApi(
    username = username,
    password = password
)


file_path = 'data/data.csv'
df = pd.read_csv(file_path)
df['Date'] = pd.to_datetime(df['Date'])
df['Total'] = df['Numbers']
df['Total'].replace(',', '', regex=True, inplace=True)

df['Total'] = df['Total'].astype(int)
df = df[['Date', 'Total']].sort_values(by='Date', ascending=True)


def time_stamp_interval(date):
  time_stamp_list = []
  for i in range(0,26,2):
    time_stamp = date + dt.timedelta(hours=i)
    time_stamp = time_stamp.timestamp()
    time_stamp = int(time_stamp)
    time_stamp_list.append(time_stamp)
  return time_stamp_list


def find_ICAO(ICAO, open_sky_data):
  total = []
  count = 0
  for i in open_sky_data:
    if i.estDepartureAirport in ICAO:
      count += 1
  total.append(count)
  totaled = np.array(total).sum()
  return totaled



year = 2025
date = df['Date']
filepath = f'data/{year}.csv'

def flight_df(dates):
  interval_list = time_stamp_interval(dates)
  int_length = len(interval_list)
  departure_list = []
  futures = []
  for k in range(0, int_length-1):
    try:
      departure_inputs = (interval_list[k], interval_list[k+1])
      departures = executor.submit(api.get_flights_from_interval,*departure_inputs)
      futures.append(departures)

    except Exception as e:
      print(f'Error: {e}')
  for future in futures:
   output = future.result()
   total_flights = find_ICAO(ICAO=ICAO, open_sky_data=output)
   departure_list.append(total_flights)
  total_departures = np.array(departure_list).sum()
  return total_departures

if __name__ == "__main__":

  start_time = time.time()

  start_time = time.time()
  executor = ThreadPoolExecutor()
  futures = []


  date_period = df[df['Date'].dt.year == year].Date.iloc[3:5]
  for i in date_period:
    future = executor.submit(flight_df, (i))
    futures.append(future)

  for date, future in zip(date_period, futures):
    print_future = future.result()
    date = date.strftime('%Y-%m-%d')

    with open(filepath, 'a', newline='') as file:
      writer = csv.writer(file)
      
      writer.writerow([date, print_future])
  

  print("--- %s seconds ---" % (time.time() - start_time))
