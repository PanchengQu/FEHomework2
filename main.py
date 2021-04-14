# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pickle

from os import listdir, remove

import pandas as pd
from bs4 import BeautifulSoup
import requests
import statsmodels.api as sm
from sklearn import linear_model
from datetime import datetime
from helper import checkperformance



def fetch_usdt_rates(YYYY):
    # Requests the USDT's daily yield data for a given year. Results are
    #   returned as a DataFrame object with the 'Date' column formatted as a
    #   pandas datetime type.

    URL = 'https://www.treasury.gov/resource-center/data-chart-center/' + \
          'interest-rates/pages/TextView.aspx?data=yieldYear&year=' + str(YYYY)

    cmt_rates_page = requests.get(URL)

    soup = BeautifulSoup(cmt_rates_page.content, 'html.parser')

    table_html = soup.findAll('table', {'class': 't-chart'})

    df = pd.read_html(str(table_html))[0]
    df.Date = pd.to_datetime(df.Date)

    return df

treasury2019=fetch_usdt_rates(2019)
treasury2020=fetch_usdt_rates(2020)
treasury2021=fetch_usdt_rates(2021)

treasurydata=pd.concat([treasury2019,treasury2020,treasury2021],axis=0)
treasurydata.reset_index(drop=True,inplace=True)

indexdrop=treasurydata[treasurydata.index<50].index

treasurydata.drop(indexdrop,inplace=True)
treasurydata.reset_index(drop=True,inplace=True)

print(treasurydata.head(5))

#Stockdata include open high low close volume and Moving Average
stockdata=pd.read_csv('IVV.csv')
VIXindex=pd.read_csv('VIX.csv')
dollarindex=pd.read_csv('DX.csv')
dollarindex.fillna(method='ffill',inplace=True)
dollarindex['Date']=pd.to_datetime(dollarindex['Date'])
dollarindex.set_index('Date',inplace=True)

VIXindexclose=list(VIXindex['Close'])

dollarindexclose=dollarindex['Close']
dollarindexclose.columns=['DI']


twoweekMV=[]
for i in range(10,len(stockdata)):
    twoweekMV.append(stockdata.iloc[i-10:i]['Open'].mean())

startindex=stockdata[stockdata['Date']=='2019-03-15'].index
indexdrop2=stockdata[stockdata.index<10].index
stockdata.drop(indexdrop2,inplace=True)
stockdata['Date']=pd.to_datetime(stockdata['Date'])
stockdata['2weeksMV']=twoweekMV

stockdata.reset_index(drop=True,inplace=True)

treasurydata.set_index('Date',inplace=True)

stockdata.set_index('Date',inplace=True)

mergedata=stockdata.join(treasurydata)
mergedata['VIX']=VIXindexclose
mergedata['DI']=dollarindexclose

mergedata.drop(['Adj Close'],axis=1,inplace=True)

#move up one daywe
mergedata['TargetClose']=mergedata['Close']
mergedata['TargetClose']=mergedata['TargetClose'].shift(periods=-1)
print(len(mergedata))

mergedata.drop(mergedata.tail(1).index,inplace=True)
mergedata.dropna(axis=0,inplace=True)

print(mergedata)
print(mergedata.columns)

#now we need X data and Y data
X=mergedata.drop(['TargetClose'],axis=1)


Y=mergedata['TargetClose']
Y.columns=['TargetClose']
print(Y)

X_train=X[:450]
X_test=X[450:]



Y_train=Y[:450]
Y_test=Y[450:]
print(Y_train)




X_train=sm.add_constant(X_train)



model=sm.OLS(Y_train,X_train)
result=model.fit()

print(result.summary())


X_test=sm.add_constant(X_test)
Y_predict=result.predict(X_test)

checkperformance(list(Y_predict),list(Y_test))

print(Y_predict)
print(Y_test)



#remove insignificant columns
removecolumns=['Volume','2 mo','3 mo', '6 mo', '1 yr','2 yr','3 yr','10 yr','20 yr']


X_train.drop(removecolumns,axis=1,inplace=True)
X_test.drop(removecolumns,axis=1,inplace=True)

model2=sm.OLS(Y_train,X_train)
result2=model2.fit()

print(result2.summary())

print(X_test)
Y_predict2=result2.predict(X_test)


print(checkperformance(list(Y_predict2),list(Y_test)))


###
removecolumns2=['1 mo','5 yr','7 yr','30 yr']
X_train.drop(removecolumns2,axis=1,inplace=True)
X_test.drop(removecolumns2,axis=1,inplace=True)
model3=sm.OLS(Y_train,X_train)
result3=model3.fit()
pickle.dump(result3,open("trainedModel",'wb'))
loadedResult = pickle.load(open("trainedModel","rb"))

print(result3.summary())
Y_predict3=result3.predict(X_test)


print(checkperformance(list(Y_predict3),list(Y_test)))







#volume, 10 year treasure yield, 1 year treasury yield, federal interest rate

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
