from ib_insync import *
from time import sleep
import pandas as pd
from helper import *
import pickle
import requests
import statsmodels.api as sm
sampling_rate = 1 # How often, in seconds, to check for inputs from Dash?
# For TWS Paper account, default port is 7497
# For IBG Paper account, default port is 4002
port = 7497
# choose your master id. Mine is 10645. You can use whatever you want, just set it in API Settings within TWS or IBG.
master_client_id = 55555
# choose your dedicated id just for orders. I picked 1111.
orders_client_id = 1515
# account number: you'll need to fill in yourself. The below is one of my paper trader account numbers.
acc_number = 'DU3530728'
########################################################################################################################

# Run your helper function to clear out any io files left over from old runs


# Create an IB app; i.e., an instance of the IB() class from the ib_insync package
ib=IB()
# Connect your app to a running instance of IBG or TWS
ib.connect(host='127.0.0.1', port=port, clientId=master_client_id)
# Make sure you're connected -- stay in this while loop until ib.isConnected() is True.
while not ib.isConnected():
    sleep(.01)


# If connected, script proceeds and prints a success message.
print('Connection Successful!')
contract=Stock("IVV",'SMART','USD')
bars = ib.reqHistoricalData(
        contract, # <<- pass in your contract object here
        endDateTime='', durationStr='10 D', barSizeSetting='1 day', whatToShow='MIDPOINT', useRTH=True
    )

# Code goes here...
bars=pd.DataFrame(bars)
twoweeksMV=bars['close'].mean()

VIX=fetch_VIX_rates()
DI=fetch_DI_rates()
d = {'const':[1.0],'Open':bars['open'][0],'High':bars['high'][0],'Low':bars['low'][0],'Close':bars['close'][0],'2weeksMV':[twoweeksMV],'VIX':[VIX],'DI':[DI]}
Predict_X = pd.DataFrame(d)
model = pickle.load(open("trainedModel","rb"))
y = model.predict(Predict_X)
print(y[0])
type(y)
contract = Stock("IVV","SMART","USD")

num = bars['close'][0]
if y[0] > num:
    order = MarketOrder("BUY", "100")
else:
    order = MarketOrder("SELL","100")
order.accoun = acc_number
ib_orders = IB()
ib_orders.connect(host = '127.0.0.1',port= port, clientId = orders_client_id)
ib_orders.placeOrder(contract, order)
print(ib_orders.fills())