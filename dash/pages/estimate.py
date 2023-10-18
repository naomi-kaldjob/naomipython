import dash
import requests
import dash_bootstrap_components as dbc
from dash import Dash, dcc, html, Input, Output, callback, State

fields = [
    {'type': 'number', 'label' : 'Nombre de lot', 'id': 'nb-lots'},
    {'type': 'number', 'label' : 'Nombre de pièces principales', 'id': 'nb-pieces'}
]

dash.register_page(__name__)
form = dbc.Row(
    [
        dbc.Col(
            dbc.FormFloating([
                dbc.Input(type=f['type'], id=f['id'], placeholder=f['label']),
                dbc.Label(f['label']),
            ]),
            width=6,
        ) for f in fields
    ],
    className='mb-3',
)

layout = html.Div([
    form,
    dbc.Button('Primary', color='primary', id='submit-val', n_clicks=0),
    html.Div(id='container-button-basic')
], className='container')

@callback(
    Output('container-button-basic', 'children'),
    Input('submit-val', 'n_clicks'),
    [State(f['id'], 'value') for f in fields],
    prevent_initial_call=True
)
def update_output(n_clicks, value, value2):
    response = requests.get(f'http://127.0.0.1:5000/estimate?nb-lot={value}&nb-piece={value2}')
    response = response.json()['data']
    return f'Selon les informations fournies votre propriété est estimée à : {response}'
