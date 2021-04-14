import pandas as pd
import statsmodels.api as sm
import pickle
import datetime
def cleaning():
    IVVback=pd.read_csv('IVV-3year.csv')
    DXback=pd.read_csv('DX-3year.csv')
    VIXback=pd.read_csv('VIX-3year.csv')

    DXback=DXback[["Date","Close"]]
    VIXback=VIXback[["Date","Close"]]

    data=IVVback.merge(DXback,how='left',on='Date')
    data.columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'DX']

    data=data.merge(VIXback,how='left',on='Date')
    data.columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume', 'DX','VIX']
    data.dropna(axis=0,inplace=True)
    data.drop(['Adj Close','Close_y','Date'],axis=1,inplace=True)
    data.columns=['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'DX','VIX']
    pickle.dump(data,open("backtest_data","wb"))
    return
def backtest_calculation(index):
    returns = list()
    data = pickle.load(open("backtest_data","rb"))
    i = index
    train = data[i:i + 242]
    test = data[i + 242:i + 273]
    train_X = train.drop(['Close'], axis=1)
    train_Y = train['Close']
    train_Y.columns = ['Close']
    test_X = test.drop(['Close'], axis=1)
    test_Y = test['Close']
    test_Y.columns = ['Close']

    train_X = sm.add_constant(train_X)
    model = sm.OLS(train_Y, train_X)
    result = model.fit()

    test_X = sm.add_constant(test_X)
    position = 0
    cash = 100000
    blotter = pd.DataFrame()
    ledger = pd.DataFrame()
    #blotter:id, date, type, act, order price, symbol, shares
    #ledger: date, position, cash, stock value, total value, return
    for j in range(0, len(test_Y)):
        prediction = result.predict(test_X.iloc[[j]]).iloc[0]
        shares = 0
        actn = ""
        if prediction > test_Y.iloc[j]:
            actn = "BUY"
            if position >= 0:
                shares = 100
            else:
                shares = -position
        else:
            actn = "SELL"
            if position <= 0:
                shares = -100
            else:
                shares = -position
        cash -= shares * test_Y.iloc[j]
        position += shares
        blotterData = [j, datetime.today(), "IVV", actn, shares, test_Y.iloc[j], "MKT"]
        blotter = blotter.append(pd.DataFrame(blotterData, columns=['id', 'date', 'symb', 'actn', 'size', 'price', 'type']))
        total = cash + position * test_Y.iloc[j]
        ledgerData = [j, datetime.today(), position, cash, position * test_Y.iloc[j], total, (total)/100000*100]
        ledger = ledger.append(pd.DataFrame(ledgerData, columns=['id','date','position','cash','stock value','total value','return(%)']))
    return ledger, blotter



