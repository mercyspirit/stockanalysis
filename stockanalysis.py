import json
import math
import matplotlib.pyplot as plt
import sys
import requests
import yfinance as yf

#   Author: Arden Qiu
#   Email: ziying.qiu@gmail.com

# gets all info about a stock
def getStockInfo():
	msft = yf.Ticker("MSFT")
	return msft.info

# Should be below 15
def priceToEarningsRatio():
	msft = yf.Ticker("MSFT")
	return msft.info['trailingPE']

def getBalanceSheet():
	req = requests.get('https://financialmodelingprep.com/api/v3/financials/balance-sheet-statement/MSFT')
	return req.json()

def getIncomeStatement():
	req = requests.get('https://financialmodelingprep.com/api/v3/financials/income-statement/MSFT')
	return req.json()

def getLatestProfit():
	income_statement = getIncomeStatement()['financials']
	return income_statement[0]['Gross Profit']

def getLastYearsProfit():
	income_statement = getIncomeStatement()['financials']
	return income_statement[1]['Gross Profit'] 

def getFinancials():
	sheet = getBalanceSheet()
	return sheet['financials']

def getLatestFinancials():
	financials = getFinancials()
	latest_financial = financials[0]
	return latest_financial

def getQuarterlyFinancials():
	msft = yf.Ticker("MSFT")
	return msft.quarterly_financials

def getActions():
	msft = yf.Ticker("MSFT")
	return msft.actions

def getEarnings():
	msft = yf.Ticker("MSFT")
	return msft.earnings

def getTotalAssets():
	latest_financial = getLatestFinancials()
	return latest_financial['Total assets']

def getTotalDebt():
	latest_financial = getLatestFinancials()
	return latest_financial['Total debt']

def getNetCurrentAssets():
	latest_financial = getLatestFinancials()
	return float(latest_financial['Total current assets']) - float(latest_financial['Total current liabilities'])

def getLongTermDebt():
	latest_financial = getLatestFinancials()
	return latest_financial['Long-term debt']

def getBookValue():
	latest_financial = getLatestFinancials()
	total_assets = float(latest_financial['Total assets'])
	total_liabilities = float(latest_financial['Total liabilities'])
	return (total_assets - total_liabilities)

def getEnterpriseValue():
	req = requests.get('https://financialmodelingprep.com/api/v3/enterprise-value/MSFT')
	return req.json()

def getLatestEnterpriseValue():
	enterprise_values = getEnterpriseValue()['enterpriseValues']
	return enterprise_values[0]

def getNumberOfShares():
	enterprise_value = getLatestEnterpriseValue()
	return enterprise_value['Number of Shares']

def getBookValuePerShare():
	return getBookValue() / float(getNumberOfShares())

def getHistory():
	msft = yf.Ticker("MSFT")
	return msft.history("1d")

def getLatestCloseHistory():
	msft = yf.Ticker("MSFT")
	return msft.history("1d")['Close'][0]

# Should be below 1.5
def priceToBookRatio():
	result = getLatestCloseHistory() / getBookValuePerShare()
	status = "FAIL"
	if result < 1.5:
		status = "PASS"
	else:
		status = "FAIL"
	return (result, status)

# Should be twice as many assets as debts
def assetsToDebts():
	result = float(getTotalAssets()) / float(getTotalDebt())
	status = "FAIL"
	if result >= 2:
		status = "PASS"
	else:
		status = "FAIL"
	return (result, status)

# Should be lower than net current assets (company could pay off debt with short term capital)
def longTermDebtToNetCurrentAssets():
	result = float(getLongTermDebt()) / float(getNetCurrentAssets())
	status = "FAIL"
	if result < 1:
		status = "PASS"
	else:
		status = "FAIL"
	return (result, status)

# profits should grow in the last year
def profitsGrew():
	result = float(getLatestProfit()) - float(getLastYearsProfit())
	status = "FAIL"
	if result > 0:
		status = "PASS"
	else:
		status = "FAIL"
	return (result, status)

# Processes the raw historical stock data json and gets a list of dates and a list of prices
def getDatesandPriceFromHistoricalStockData(historicalStockData, type):
	dateList = []
	priceList = []

	for day in historicalStockData:
		dateList.append(str(day['date']))
		priceList.append(day[type])
	return (dateList, priceList)

def displayGraph(historicalStockData, sticker, duration="1m"):
	dateList = []
	priceList = []

	# chart
	for day in historicalStockData:
		dateList.append(str(day['date']))
		priceList.append(day['open'])

	plt.plot(dateList, priceList)
	plt.xlabel('Dates')
	plt.ylabel('Open')
	plt.show()

def expectedReturnAndPriceProbability(historicalStockData):
	priceList = []
	priceCount = {}
	priceAndProbabilityList = {}
	expectedReturn = 0.0
	# chart
	for day in historicalStockData:
		priceList.append(day['open'])

	for price in priceList:
		priceAsString = str(price)
		if priceAsString in priceCount:
			priceCount[priceAsString] = priceCount.get(priceAsString) + 1
		else:
			priceCount[priceAsString] = 1
	totalLength = len(priceCount)

	for price,count in priceCount.items():
		probability = float(count)/float(totalLength)
		priceAndProbabilityList[price] = probability
		probabilityAndPrice = probability * float(price)
		expectedReturn += probabilityAndPrice

	
	return (expectedReturn, priceAndProbabilityList)

def variance(expectedReturn, priceAndProbabilityList):
	variance = 0.0
	for price,probability in priceAndProbabilityList.items():
		diff = float(price) - expectedReturn
		diff = diff ** 2
		variance = variance + (diff * probability)

	return variance

def covariance(historicalStockDataOne, historicalStockDataTwo):
	return

print("Price to Book Ratio: %.10f, %s" % (priceToBookRatio()))
print("Assets To Debts: %.10f, %s" % (assetsToDebts()))
print("Long Term Debt to Net Current Assets: %.10f, %s" % (longTermDebtToNetCurrentAssets()))
print("Profits Grew: %.10f, %s" % (profitsGrew()))
# stockanalysis -C company name -D duration
#companySticker = sys.argv[2]
#duration = sys.argv[4]
#historicalStockData = getStockData(companySticker, "1m")
#print(companySticker)
#displayGraph(historicalStockData, companySticker, duration)
#expectedReturnAndPriceProbabilityTuple = expectedReturnAndPriceProbability(historicalStockData)
#expectedReturn = expectedReturnAndPriceProbabilityTuple[0]
#priceAndProbabilityList = expectedReturnAndPriceProbabilityTuple[1]
#standarddeviation = math.sqrt(variance(expectedReturn,priceAndProbabilityList))
#print(standarddeviation)