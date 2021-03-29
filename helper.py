import pandas as pd
from bs4 import BeautifulSoup
import requests
def checkperformance(predict,real):
    diffpredict=[]
    diffreal=[]
    correct=0
    for i in range(len(predict)-1):
        diffpredict.append(predict[i+1]-predict[i])
        diffreal.append(real[i+1]-real[i])
    for i in range(len(diffreal)):
        if diffreal[i]>=0 and diffpredict[i]>=0:
            correct=correct+1
        elif diffreal[i]<0 and diffpredict[i]<0:
            correct=correct+1
        else:
            continue
    return correct/(len(diffreal)-1)


def fetch_VIX_rates():
    # Requests the USDT's daily yield data for a given year. Results are
    #   returned as a DataFrame object with the 'Date' column formatted as a
    #   pandas datetime type.

    URL = 'https://finance.yahoo.com/quote/%5EVIX/history/'

    cmt_rates_page = requests.get(URL)

    soup = BeautifulSoup(cmt_rates_page.content, 'html.parser')

    table_html = soup.findAll('table', {'class': 'W(100%) M(0)'})

    df = pd.read_html(str(table_html))[0]


    return float(df['Close*'][0])

def fetch_DI_rates():
    # Requests the USDT's daily yield data for a given year. Results are
    #   returned as a DataFrame object with the 'Date' column formatted as a
    #   pandas datetime type.

    URL = 'https://finance.yahoo.com/quote/DX-Y.NYB/history/'

    cmt_rates_page = requests.get(URL)

    soup = BeautifulSoup(cmt_rates_page.content, 'html.parser')

    table_html = soup.findAll('table', {'class': 'W(100%) M(0)'})

    df = pd.read_html(str(table_html))[0]


    return float(df['Close*'][0])

