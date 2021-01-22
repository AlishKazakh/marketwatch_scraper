import bs4 as bs
import datetime as dt
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np
import os
import pandas as pd
import pandas_datareader.data as web
import pickle
import requests
from progress.bar import Bar
import urllib.request, urllib.error, urllib.parse
import time


def save_sp500_tickers():  ###### это функция, которая сохраняет коды(названия) компаний
	resp = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
	soup = bs.BeautifulSoup(resp.text, 'lxml')
	table = soup.find('table', {'class': 'wikitable sortable', 'id': 'constituents'})
	tickers = []
	for row in table.findAll('tr')[1:]:
		ticker = row.findAll('td')[0].text
		tickers.append(ticker[:-1])
	
	with open("sp500tickers.pickle", "wb") as f:
		pickle.dump(tickers,f)
    
	return tickers

def get_data_from_marketwatch(reload_sp500 = False):  ##############  это функция, которая вытягивает финансовые показатели компаний с marketwatch  #############
	if reload_sp500:
		tickers = save_sp500_tickers()
	else:
		with open("sp500tickers.pickle","rb") as f:
			tickers = pickle.load(f)

	if not os.path.exists('stock_dfs_sec'):
		os.makedirs('stock_dfs_sec')
	
	for count,ticker in enumerate(tickers):
		if not os.path.exists('stock_dfs_sec/{}'.format(ticker)):
			os.makedirs('stock_dfs_sec/{}'.format(ticker))			
			
			resp = requests.get('https://www.marketwatch.com/investing/stock/{}/financials/secfilings/10k'.format(ticker))
			soup = bs.BeautifulSoup(resp.text,'lxml')
			body = soup.find('body')
			tables = body.findAll('tbody')
			table_class = []
			for table in tables:
				table_class.append(table.get('class')[0])

			if 'table__body' in table_class:
				table_sec = body.find('tbody', {'class': 'table__body'})
				files_id = {}

				for row in table_sec.findAll('tr'):
					year = row.findAll('td')[1].text
					doc_id = str(row.findAll('td')[2]).split("docid=")[1][:9].replace('"','').strip()
					files_id[year] = doc_id
				for keys, values in files_id.items():
					response = urllib.request.urlopen('https://www.marketwatch.com/investing/stock/{}/SecArticle?guid={}'.format(ticker,values))
					webContent = response.read()
					keys = keys.replace('/','_')
					#print(keys)
					#print("stock_dfs_sec/{}/{}_financial_statement_{}.html".format(ticker,keys))
					if not os.path.exists('stock_dfs_sec/{}/{}_financial_statement_{}.html'.format(ticker,ticker,keys)):
						f = open("stock_dfs_sec/{}/{}_financial_statement_{}.html".format(ticker,ticker,keys), 'wb')
						f.write(webContent)
						f.close

					time.sleep(1)

			else:
				print("There is no available financial data for {}".format(ticker))
				continue

		print("{}. {} loaded. {}%".format(count+1,ticker,(count+1)/5))

			
						
					
### я должен буду объединить вытягивание данных для трех категорий и поправить код, чтобы вытягивал данные правильно


#save_sp500_tickers()
get_data_from_marketwatch()	



