import pandas as pd
import statsmodels.api as sm

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
returns = list()
for i in range(0,len(data)-273):
    train = data[i:i+242]
    test = data[i+242:i+273]
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
    cash = 0
    for j in range(0,len(test_Y)):
        prediction = result.predict(test_X.iloc[[j]]).iloc[0]
        shares = 0
        if prediction > test_Y.iloc[j]:
            if position >= 0:
                shares = 100
            else:
                shares = -position
        else:
            if position <= 0:
                shares = -100
            else:
                shares = -position
        cash -= shares * test_Y.iloc[j]
        position += shares
    returns.append(cash + position * test_Y.iloc[len(test_Y)-1])

count = 0
for i in returns:
    if i > 0:
        count += 1
print(count/(len(data)-272))

