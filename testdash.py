
import dash
import plotly.graph_objects as go
import plotly.express as px
import dash_core_components as dcc
import dash_html_components as html
from dash_table import DataTable, FormatTemplate

import numpy as np
from sklearn import linear_model

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
                "n: number of days a limit order to exit a position is " + \
                "kept open"
            ),
            html.Li(
                "N: number of observed historical trading days to use in " + \
                "training the logistic regression model."
            ),
            html.Li(
                'alpha: a percentage in numeric form ' + \
                '(e.g., "0.02" == "2%") that defines the profit sought by ' + \
                'entering a trade; for example, if IVV is bought at ' + \
                'price X, then a limit order to sell the shares will be put' + \
                ' in place at a price = X*(1+alpha)'
            ),
            html.Li(
                'lot_size: number of shares traded in each round-trip ' + \
                'trade. Kept constant for simplicity.'
            ),
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
                            [html.Tr([
                                html.Th('Alpha'), html.Th('Beta'),
                                html.Th('Geometric Mean Return'),
                                html.Th('Average Trades per Year'),
                                html.Th('Volatility'), html.Th('Sharpe')
                            ])] + [html.Tr([
                                html.Td(html.Div(id='strategy-alpha')),
                                html.Td(html.Div(id='strategy-beta')),
                                html.Td(html.Div(id='strategy-gmrr')),
                                html.Td(html.Div(id='strategy-trades-per-yr')),
                                html.Td(html.Div(id='strategy-vol')),
                                html.Td(html.Div(id='strategy-sharpe'))
                            ])],
                            className='main-summary-table'
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
            style_cell={'textAlign': 'center'},
            style_table={'height': '300px', 'overflowY': 'auto'}
        )
    ]),
    html.Div([
        html.Div([
            html.H2(
                'Trade Blotter',
                style={
                    'display': 'inline-block', 'width': '55%',
                    'text-align': 'center'
                }
            )
        ]),
        html.Div(
            DataTable(
                id='blotter',
                fixed_rows={'headers': True},
                style_cell={'textAlign': 'center'},
                style_table={'height': '300px', 'overflowY': 'auto'}
            ),
            style={'display': 'inline-block', 'width': '55%'}
        )
    ]),
    # html.Div([
    #     html.Div(
    #         dcc.Graph(id='bonds-3d-graph', style={'display': 'none'}),
    #         style={'display': 'inline-block', 'width': '50%'}
    #     ),
    #     html.Div(
    #         dcc.Graph(id='candlestick', style={'display': 'none'}),
    #         style={'display': 'inline-block', 'width': '50%'}
    #     )
    # ]),
    # html.Div(id='proposed-trade'),
    ############################################################################
    ############################################################################
])
@app.callback(
    [dash.dependencies.Output('blotter', 'data'),
    dash.dependencies.Output('blotter', 'columns'),
    dash.dependencies.Output('trade-ledger', 'data'),
    dash.dependencies.Output('trade-ledger', 'columns')],
    dash.dependencies.Input("run-backtest",'n_clicks'),
    dash.dependencies.State(),
    prevent_initial_call = True
)
def update_backtest(n_clicks, startDate):

    return
# @app.callback(
#     [dash.dependencies.Output('bonds-hist', 'children'),
#      dash.dependencies.Output('bonds-3d-graph', 'figure'),
#      dash.dependencies.Output('bonds-3d-graph', 'style')],
#     dash.dependencies.Input("run-backtest", 'n_clicks'),
#     [dash.dependencies.State('hist-data-range', 'start_date'),
#      dash.dependencies.State('hist-data-range', 'end_date'),
#      dash.dependencies.State('big-N', 'value'),
#      dash.dependencies.State('lil-n', 'value')
#      ],
#     prevent_initial_call=True
# )
# def update_bonds_hist(n_clicks, startDate, endDate, N, n):
#
#     bonds_data = usdt_cmt_rates(startDate, endDate, N, n)
#
#     fig = go.Figure(
#         data=[
#             go.Surface(
#                 z=bonds_data,
#                 y=bonds_data.Date,
#                 x=[
#                     to_years(cmt_colname) for cmt_colname in list(
#                         filter(lambda x: ' ' in x, bonds_data.columns.values)
#                     )
#                 ]
#             )
#         ]
#     )
#
#     fig.update_layout(
#         scene=dict(
#             xaxis_title='Maturity (years)',
#             yaxis_title='Date',
#             zaxis_title='APR (%)',
#             zaxis=dict(ticksuffix='%')
#         )
#     )
#
#     bonds_data.reset_index(drop=True, inplace=True)
#
#     return bonds_data.to_json(), fig, {'display': 'block'}
#
#
# @app.callback(
#     [
#         dash.dependencies.Output('features-and-responses', 'data'),
#         dash.dependencies.Output('features-and-responses', 'columns'),
#         dash.dependencies.Output('blotter', 'data'),
#         dash.dependencies.Output('blotter', 'columns'),
#         dash.dependencies.Output('calendar-ledger', 'data'),
#         dash.dependencies.Output('calendar-ledger', 'columns'),
#         dash.dependencies.Output('trade-ledger', 'data'),
#         dash.dependencies.Output('trade-ledger', 'columns')
#     ],
#     [dash.dependencies.Input('ivv-hist', 'children'),
#      dash.dependencies.Input('bonds-hist', 'children'),
#      dash.dependencies.Input('lil-n', 'value'),
#      dash.dependencies.Input('big-N', 'value'),
#      dash.dependencies.Input('alpha', 'value'),
#      dash.dependencies.Input('lot-size', 'value'),
#      dash.dependencies.Input('starting-cash', 'value'),
#      dash.dependencies.State('hist-data-range', 'start_date'),
#      dash.dependencies.State('hist-data-range', 'end_date')],
#     prevent_initial_call=True
# )
# def calculate_backtest(
#         ivv_hist, bonds_hist, n, N, alpha, lot_size, starting_cash,
#         start_date, end_date
# ):
#     features_and_responses, blotter, calendar_ledger, trade_ledger = backtest(
#         ivv_hist, bonds_hist, n, N, alpha, lot_size, start_date, end_date,
#         starting_cash
#     )
#
#     features_and_responses_columns = [
#         {"name": i, "id": i} for i in features_and_responses.columns
#     ]
#     features_and_responses = features_and_responses.to_dict('records')
#
#     blotter = blotter.to_dict('records')
#     blotter_columns = [
#         dict(id='ID', name='ID'),
#         dict(id='ls', name='long/short'),
#         dict(id='submitted', name='Created'),
#         dict(id='action', name='Action'),
#         dict(id='size', name='Size'),
#         dict(id='symbol', name='Symb'),
#         dict(
#             id='price', name='Order Price', type='numeric',
#             format=FormatTemplate.money(2)
#         ),
#         dict(id='type', name='Type'),
#         dict(id='status', name='Status'),
#         dict(id='fill_price', name='Fill Price', type='numeric',
#              format=FormatTemplate.money(2)
#              ),
#         dict(id='filled_or_cancelled', name='Filled/Cancelled')
#     ]
#
#     calendar_ledger = calendar_ledger.to_dict('records')
#     calendar_ledger_columns = [
#         dict(id='Date', name='Date'),
#         dict(id='position', name='position'),
#         dict(id='ivv_close', name='IVV Close', type='numeric',
#              format=FormatTemplate.money(2)),
#         dict(id='cash', name='Cash', type='numeric',
#              format=FormatTemplate.money(2)),
#         dict(id='stock_value', name='Stock Value', type='numeric',
#              format=FormatTemplate.money(2)),
#         dict(id='total_value', name='Total Value', type='numeric',
#              format=FormatTemplate.money(2))
#     ]
#
#     trade_ledger = trade_ledger.to_dict('records')
#     trade_ledger_columns = [
#         dict(id='trade_id', name="ID"),
#         dict(id='open_dt', name='Trade Opened'),
#         dict(id='close_dt', name='Trade Closed'),
#         dict(id='trading_days_open', name='Trading Days Open'),
#         dict(id='buy_price', name='Entry Price', type='numeric',
#              format=FormatTemplate.money(2)),
#         dict(id='sell_price', name='Exit Price', type='numeric',
#              format=FormatTemplate.money(2)),
#         dict(id='benchmark_buy_price', name='Benchmark Buy Price',
#              type='numeric', format=FormatTemplate.money(2)),
#         dict(id='benchmark_sell_price', name='Benchmark sell Price',
#              type='numeric', format=FormatTemplate.money(2)),
#         dict(id='trade_rtn', name='Return on Trade', type='numeric',
#              format=FormatTemplate.percentage(3)),
#         dict(id='benchmark_rtn', name='Benchmark Return', type='numeric',
#              format=FormatTemplate.percentage(3)),
#         dict(id='trade_rtn_per_trading_day', name='Trade Rtn / trd day',
#              type='numeric', format=FormatTemplate.percentage(3)),
#         dict(id='benchmark_rtn_per_trading_day', name='Benchmark Rtn / trd day',
#              type='numeric', format=FormatTemplate.percentage(3))
#     ]
#
#     return features_and_responses, features_and_responses_columns, blotter, \
#            blotter_columns, calendar_ledger, calendar_ledger_columns, \
#            trade_ledger, trade_ledger_columns
#
#
# @app.callback(
#     [
#         dash.dependencies.Output('alpha-beta', 'figure'),
#         dash.dependencies.Output('strategy-alpha', 'children'),
#         dash.dependencies.Output('strategy-beta', 'children'),
#         dash.dependencies.Output('strategy-gmrr', 'children'),
#         dash.dependencies.Output('strategy-trades-per-yr', 'children'),
#         dash.dependencies.Output('strategy-vol', 'children'),
#         dash.dependencies.Output('strategy-sharpe', 'children')
#     ],
#     dash.dependencies.Input('trade-ledger', 'data'),
#     prevent_initial_call=True
# )
# def update_performance_metrics(trade_ledger):
#     trade_ledger = pd.DataFrame(trade_ledger)
#     trade_ledger = trade_ledger[1:]
#
#     X = trade_ledger['benchmark_rtn_per_trading_day'].values.reshape(-1, 1)
#
#     linreg_model = linear_model.LinearRegression()
#     linreg_model.fit(X, trade_ledger['trade_rtn_per_trading_day'])
#
#     x_range = np.linspace(X.min(), X.max(), 100)
#     y_range = linreg_model.predict(x_range.reshape(-1, 1))
#
#     fig = px.scatter(
#         trade_ledger,
#         title="Performance against Benchmark",
#         x='benchmark_rtn_per_trading_day',
#         y='trade_rtn_per_trading_day'
#     )
#
#     fig.add_traces(go.Scatter(x=x_range, y=y_range, name='OLS Fit'))
#
#     alpha = str(round(linreg_model.intercept_ * 100, 3)) + "% / trade"
#     beta = round(linreg_model.coef_[0], 3)
#
#     gmrr = (trade_ledger['trade_rtn_per_trading_day'] + 1).product() ** (
#             1 / len(
#         trade_ledger)) - 1
#
#     avg_trades_per_yr = round(
#         trade_ledger['open_dt'].groupby(
#             pd.DatetimeIndex(trade_ledger['open_dt']).year
#         ).agg('count').mean(),
#         0
#     )
#
#     vol = stdev(trade_ledger['trade_rtn_per_trading_day'])
#
#     sharpe = round(gmrr / vol, 3)
#
#     gmrr_str = str(round(gmrr, 3)) + "% / trade"
#
#     vol_str = str(round(vol, 3)) + "% / trade"
#
#     return fig, alpha, beta, gmrr_str, avg_trades_per_yr, vol_str, sharpe


# Run it!
if __name__ == '__main__':
    app.run_server(debug=True)