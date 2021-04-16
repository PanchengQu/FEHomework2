
import dash
import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable, FormatTemplate
import Backtest
import numpy as np
from sklearn import linear_model
from utils import *
from datetime import date, timedelta
Backtest.cleaning()
# Create a Dash app
app = dash.Dash(__name__)

# Create the page layout
app.layout = html.Div([
    html.H1(
        'Trading Strategy Example Template',
        style={'display': 'block', 'text-align': 'center'}
    ),
    html.Div([
        html.H2('Strategy'),
        html.P('This app explores a simple strategy that works as follows:'),
        html.Ol([
            html.Li([
                "We pick up the two year fixed period data of treasury data which is  " + \
                "from 2019-03-15 to 2021-03-15. To achieve this goal, we use the web scraping " +\
                "Cleaning the data by concatenate the data and drop the missing value.",
                html.Ul([
                    html.Li("IVV: daily open, high, low, & close prices"),
                    html.Li(
                        "US Treasury CMT Rates for 1 mo, 2 mo, 3 mo, 6 mo, " + \
                        "1 yr and 2 yr maturities."
                    ),
                     html.Li(
                        "VIX index, dollar index and 2 weeks moving average"
                    )

                ])
            ]),
            html.Li([
                'We got the whole dataframe after cleaning and merging. ' + \
                'The next step is to split it to test dataset and train dataset. ' +\
                'Using linear regression to do the prediction.'
                ,
                html.Ul([
                    html.Li('the y-intercept ("a")'),
                    html.Li('the slope ("b")'),
                    html.Li('the P value for each variable'),
                    html.Li('the coefficient of determination ("R^2")')
                ]),

            ]),
            html.Li([
                'Drop the variable whose p value is significant larger than 0.05 ' + \
                'We believe those variables are not helpful. ' +\
                'The final variables we intend to use are',
                html.Ul([
                    html.Li('Open, High, Low, Close,'),
                    html.Li('2 weeks moving average price'),
                    html.Li('VIX index'),
                    html.Li('Dollar index')
                ]),
            ]),
            html.Li(
                'The main goal here is to use these variable to predict Closed price in tomorrow'

            ),
            html.Li(
                'The basic result of action is that, if predicted tomorrow closed price ' + \
                'is greater than today’s closed price. We will make ' + \
                'the buy action for 100 shares. However, if we have positive ' + \
                'position and predict that tomorrow’s closed price ' + \
                'will be lower, then we will closed the position. We also did the same thing to short the stock.'
            ),
            html.Li(
                'We also did the same thing to short the stock ' + \
                'if predicted tomorrow closed price ' + \
                'is lower than today’s closed price. We will make ' + \
                'the sell action for 100 shares. However, if we have negative ' + \
                'position and predict that tomorrow’s closed price  ' + \
                'will be higher, then we will closed the position.'
            ),


        ])
    ],
        style={'display': 'inline-block', 'width': '50%'}
    ),
    html.Div([
        html.H2('Data Sources Disclaimer'),
        html.P(
            'This Dash app makes use of Yahoo Finance\'s data which including ' + \
            'historical open, high, low, close price, IVV and dollar index' + \
            'The bond data is web scrapping from the US government official website ' + \
            'which are publicly available information on ' + \
            'the Internet '

        ),
        html.H2('Parameters'),
        html.Ol([
            html.Li(
                'date_range: Date range over which to perform the backtest.'
            )
        ]),
        html.Div(
            [
                html.Div(
                    [
                        html.Button(
                            "RUN BACKTEST", id='run-backtest', n_clicks=0
                        ),
                        html.Table(
                            # Header
                            [html.Tr([
                                html.Th('Date Range'),
                                html.Th('Starting Cash')
                            ])] +
                            # Body
                            [html.Tr([
                                html.Td(
                                    dcc.DatePickerSingle(
                                        id='hist-data-range',
                                        min_date_allowed=date(2019, 3, 18),
                                        max_date_allowed=date(2021,3,6),
                                        initial_visible_month=date.today(),
                                        date=date(2019, 4, 1)
                                    )
                                ),
                                html.Td(
                                    dcc.Input(
                                        id="starting-cash", type="number",
                                        value=100000,
                                        style={'text-align': 'center',
                                               'width': '100px'}
                                    )
                                )
                            ])]
                        )
                    ],
                    style={'display': 'inline-block', 'width': '50%'}
                )
            ],
            style={'display': 'block'}
        )
    ],
        style={
            'display': 'inline-block', 'width': '50%', 'vertical-align': 'top'
        }
    ),
    ##### Intermediate Variables (hidden in divs as JSON) ######################
    ############################################################################
    # Hidden div inside the app that stores IVV historical data
    html.Div(id='ivv-hist', style={'display': 'none'}),
    # Hidden div inside the app that stores bonds historical data
    html.Div(id='bonds-hist', style={'display': 'none'}),
    ############################################################################
    ############################################################################
    # html.Div(
    #     [dcc.Graph(id='alpha-beta')],
    #     style={'display': 'inline-block', 'width': '50%'}
    # ),
    # Display the current selected date range
    html.Div(id='date-range-output'),
    html.Div([
        html.H2(
            'Trade Ledger',
            style={
                'display': 'inline-block', 'text-align': 'center',
                'width': '100%'
            }
        ),
        DataTable(
            id='trade-ledger',
            fixed_rows={'headers': True},
            #style_cell={'textAlign': 'center'},
            style_table={'height': '300px', 'overflowY': 'auto'}
        )
    ]),
    html.Div([
        html.H2(
            'Trade Blotter',
            style={
                'display': 'inline-block', 'width': '100%',
                'text-align': 'center'
            }
        ),
        DataTable(
            id='blotter',
            fixed_rows={'headers': True},
            #style_cell={'textAlign': 'center'},
            style_table={'height': '300px', 'overflowY': 'auto'}
        ),
    ]),

])
@app.callback(
    [dash.dependencies.Output('blotter', 'data'),
    dash.dependencies.Output('blotter', 'columns'),
    dash.dependencies.Output('trade-ledger', 'data'),
    dash.dependencies.Output('trade-ledger', 'columns')],
    dash.dependencies.Input("run-backtest",'n_clicks'),
    dash.dependencies.State("hist-data-range",'date'),
    prevent_initial_call = True
)
def update_backtest(n_clicks, startDate):
    print(startDate)
    ledger, blotter = Backtest.backtest_calculation(startDate)
    print(ledger, blotter)
    print(blotter)
    blotter_columns = [{'id': c, 'name': c} for c in blotter.columns]
    blotter = blotter.to_dict('records')
    ledger_columns = [{'id': c, 'name': c} for c in ledger.columns]
    ledger = ledger.to_dict('records')
    return blotter, blotter_columns, ledger, ledger_columns

# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)