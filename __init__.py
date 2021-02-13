import datetime
import logging
import requests
import json
import pandas
import pyodbc
from datetime import datetime


import azure.functions as func
from . import DeGiro


def main(mytimer: func.TimerRequest) -> None:
    timestmp = datetime.now() #In PowerBI there is a query that depends on this being constant for each run. Don't change, otherwise PBI will break
    # Fix this to use Azure Vault instead of hardcoded creds. 
    FetchDataForSingleAccount('DEGIRO_USERNAME', 'DEGIRO_PASSWORD', 'SQL_USERNAME', 'SQL_PASSWORD', timestmp)
    
def FetchDataForSingleAccount(dg_username, dg_password, db_username, db_password, timestmp) -> None:
    cnxn = pyodbc.connect(f'Driver={{ODBC Driver 17 for SQL Server}};Server=tcp:DATABASE_ADRESS,1433;Database=Investments;Uid={db_username};Pwd={db_password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')
    if (cnxn is None):
        logging.error("Failed to connect to SQL database")
        return
    
    cursor = cnxn.cursor()
    if (cursor is None):    
        logging.error("Failed to select cursor in SQL database")
        return

    dg = DeGiro.DeGiro()
    dg.login(dg_username, dg_password)

    
    portfolio = dg.getdata(DeGiro.Data.Type.RAW_PORTFOLIO, False)
    if (portfolio is None):
        logging.error("Failed to get portfolio data")
        return

    for rows in portfolio['portfolio']['value']:
        pd = dg.product_info(rows['id'])
        rows['data']=pd

        #unfold the weird 'values' struct
        for subrows in rows['value']:
            if subrows['name'] == 'value': #prevent overwriting the 'value' item with an inner value item. 
                key = 'productValue'
            else:
                key = subrows['name']
            
            if key == "accruedInterest" and not('value' in subrows):
                value = 0
            elif key == "plBase" or key == "todayPlBase":
                value = subrows['value']['EUR']
            else:
                value = subrows['value']
            rows[key] = value
        #delete the old values struct
        del rows['value']

        #unfold the data struct
        for data_key in rows['data'].keys():
            #ignore some subtypes we dont care about.
            if (data_key == 'id' or data_key == 'orderTimeTypes' or data_key == 'buyOrderTypes' or 
               data_key == 'sellOrderTypes' or data_key == 'productBitTypes'):
                continue

            #prevent a clash with an existing 'name' property. 
            if data_key == 'name':
                key = 'productName'
            else:
                key = data_key
            
            rows[key] = rows['data'][data_key]
        del rows['data']

    query = "SELECT id FROM [dbo].[Portfolios] WHERE dg_username = ?"

    cursor.execute(query, dg.client_username) 
    row = cursor.fetchone() 
    portfolioDBId = -1
    if row: 
        portfolioDBId = row[0]

    if portfolioDBId == -1:
        logging.error("The username is not known in the database. Please add a portfolio in [dbo].[Portfolios].")
        return

    query = """
INSERT INTO [dbo].[PortfolioLines]
    ([portfolioId]
    ,[timestamp]
    ,[dg_isin]
    ,[dg_productName]
    ,[dg_symbol]
    ,[dg_productId]
    ,[dg_isAdded]
    ,[dg_positionType]
    ,[dg_size]
    ,[dg_price]
    ,[dg_productValue]
    ,[dg_accruedInterest]
    ,[dg_plBase]
    ,[dg_todayPlBase]
    ,[dg_portfolioValueCorrection]
    ,[dg_breakEvenPrice]
    ,[dg_averageFxRate]
    ,[dg_realizedProductPl]
    ,[dg_realizedFxPl]
    ,[dg_todayRealizedProductPl]
    ,[dg_todayRealizedFxPl]
    ,[dg_contractSize]
    ,[dg_productType]
    ,[dg_productTypeId]
    ,[dg_category]
    ,[dg_currency]
    ,[dg_exchangeId]
    ,[dg_onlyEodPrices]
    ,[dg_closePrice]
    ,[dg_closePriceDate])
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
"""

    for rows in portfolio['portfolio']['value']:
        cursor.execute(query, 
                        portfolioDBId, 
                        timestmp, 
                        rows["isin"], 
                        rows["productName"],
                        rows["symbol"],
                        rows["id"],
                        rows["isAdded"],
                        rows["positionType"],
                        rows["size"],
                        rows["price"],
                        rows["productValue"],
                        rows["accruedInterest"],
                        rows["plBase"],
                        rows["todayPlBase"],
                        rows["portfolioValueCorrection"],
                        rows["breakEvenPrice"],
                        rows["averageFxRate"],
                        rows["realizedProductPl"],
                        rows["realizedFxPl"],
                        rows["todayRealizedProductPl"],
                        rows["todayRealizedFxPl"],
                        rows["contractSize"],
                        rows["productType"] if ("productType" in rows) else None,
                        rows["productTypeId"],
                        rows["category"] if ("category" in rows) else None,
                        rows["currency"],
                        rows["exchangeId"],
                        rows["onlyEodPrices"] if ("onlyEodPrices" in rows) else None,
                        rows["closePrice"] if ("closePrice" in rows) else None,
                        rows["closePriceDate"] if ("closePriceDate" in rows) else None)
    
    cnxn.commit()

    logging.info(f'Data retrieved for account {dg.client_username} at {datetime.now()}')