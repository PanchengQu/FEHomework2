import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd

app = dash.Dash(__name__)

# Define the layout of the dash page.'


app.layout = html.Div([
    dcc.Textarea(
        id='textarea-example',
        value='Textarea content initialized\nwith multiple lines of text',
        style={'width': '50%', 'height': 300},
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)
