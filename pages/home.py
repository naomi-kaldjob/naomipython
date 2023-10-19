
import pandas as pd
import plotly.express as px
import dash
from dash import Dash, html, dcc, callback, Output, Input
import json

years = [18, 19, 20, 21]


df_2018=pd.read_csv(f'./data/valeursfoncieres-2018.txt', sep='|', decimal=',', nrows=10000, low_memory=False)
df_2019=pd.read_csv(f'./data/valeursfoncieres-2019.txt', sep='|', decimal=',', nrows=10000, low_memory=False)
df_2020=pd.read_csv(f'./data/valeursfoncieres-2019.txt', sep='|', decimal=',', nrows=10000, low_memory=False)
df_2021=pd.read_csv(f'./data/valeursfoncieres-2020.txt', sep='|', decimal=',', nrows=10000, low_memory=False)
    
df = pd.concat([df_2018,df_2019,df_2020,df_2021])
dfC = df.copy()
df.shape

dfAddress = pd.read_csv('./data/communes-departement-region.csv', sep=',')
dfAddress = dfAddress.drop_duplicates(subset=['code_departement'])

dfRegions = pd.DataFrame(dfAddress.code_region.ffill().unique(), columns=['code_region'])
dfRegions.code_region = dfRegions.code_region.astype('int').astype('str').str.pad(2, side='left', fillchar='0')


dfDepts = pd.DataFrame(dfAddress.code_departement.ffill().unique(), columns=['code_departement'])
dfDepts.code_departement = dfDepts.code_departement.astype('str').str.pad(2, side='left', fillchar='0')

dfScales = {'region': dfRegions, 'departement': dfDepts}

geojson = {}


with open('./data/metropole-version-simplifiee.geojson') as response:
    geojson['metropole'] = json.load(response)

with open('./data/regions-version-simplifiee.geojson') as response:
    geojson['region'] = json.load(response)

with open('./data/departements-version-simplifiee.geojson') as response:
    geojson['departement'] = json.load(response)

df['key'] = df['Date mutation'].astype('str') + df['Type de voie'].astype('str') + df['Voie'].astype('str') + df['Code postal'].astype('str')
df = df.groupby('key').filter(lambda x : len(x) == 1)


df = df[df['Valeur fonciere'] > 1]
df = df[df['Type local'].notna()]

missingValueRate = df.isna().mean() * 100
df = df[df.columns[missingValueRate < 65]]

df.drop(['No disposition', 'No plan', 'Section', 'Nature culture'], axis=1, inplace=True)

df['Date mutation'] = pd.to_datetime(df['Date mutation'], format="%d/%m/%Y")
df['annee'] = df['Date mutation'].dt.year
df['mois'] = df['Date mutation'].dt.month

df['Code departement'] = df['Code departement'].astype('str').str.pad(2, side='left', fillchar='0')
dfAddress['code_departement'] = dfAddress['code_departement'].astype('str').str.pad(2, side='left', fillchar='0')

df = df.merge(dfAddress.loc[:, ['code_departement', 'code_region', 'nom_region', 'latitude', 'longitude']], how='left', left_on='Code departement', right_on='code_departement')

df['code_region'] = df['code_region'].astype('int').astype('str').str.pad(2, side='left', fillchar='0')

echelle = {
    'Departement': 'departement',
    'Region' : 'region',
}

filterStyle = {
    'display': 'flex',
    'alignItems': 'center',
    'gap': '8px'
}
dropdownStyle = {
    'width': '200px'
}
cardStyle = {
    'padding': '10px',
    'display': 'flex',
    'borderRadius': '8px',
    'textAlign': 'center',
    'width': '30%',
    'boxShadow': 'rgba(99, 99, 99, 0.2) 0px 2px 8px 0px',
    'flexDirection': 'column',
    'gap': '8px',
}

def inputTolist(value):
    if(type(value) == str):
        return [int(value)]
    else:
        return [int(x) for x in value]

dash.register_page(__name__, path='/')

layout = html.Div([
    html.Div([
        html.Div([
            html.Label(children='Année'),
            dcc.Dropdown(df['annee'].unique(), '2018', id='years-selection', style=dropdownStyle, multi=True),
        ], style=filterStyle),

        html.Div([
            html.Label(children='Echelle'),
            dcc.Dropdown(list(echelle.keys()), 'Departement', id='scale-selection', style={'width': '150px'}),
        ], style=filterStyle),
    ], style={'display':'flex', 'gap': '16px'}),

    html.Div([
        html.Div([
            html.H3(children='Total de vente', style={'margin': '0'}),
            html.Label(id='nb-vente', style={'fontSize': '24px'})
        ], style=cardStyle),

        html.Div([
            html.H3(children='Moyenne des valeurs foncières', style={'margin': '0'}),
            html.Label(id='avg-vente', style={'fontSize': '24px'})
        ], style=cardStyle)
    ], style={'display': 'flex', 'margin': '32px 0', 'gap': '16px'}),
    html.Div([
        html.Div([
            dcc.Graph(id='graph-content', style={'height':'400px'}),
            dcc.Graph(id='graph-bar')
        ], style={ 'width' : '60%', }),
        html.Div([
            dcc.Graph(id='graph-map')
        ], style={ 'width' : '40%', }),
    ], style={ 'display' : 'flex', }),
    html.Div([
        html.Div([
            dcc.Graph(id='pie-chart-local'),
        ], style={ 'width' : '30%', }),
        html.Div([
            dcc.Graph(id='pie-chart-mutation')
        ], style={ 'width' : '30%', }),
    ], style={ 'display' : 'flex', })
], className='mx-3')


@callback(
    Output('nb-vente', 'children'),
    Input('years-selection', 'value')
)
def update_stats(value):
    years =inputTolist(value)
    dff = df[df['annee'].isin(years)]
    return dff.shape[0]


@callback(
    Output('avg-vente', 'children'),
    Input('years-selection', 'value')
)
def update_stats(value):
    years =inputTolist(value)
    dff = df[df['annee'].isin(years)]
    return round(dff['Valeur fonciere'].mean(), 2)


@callback(
    Output('graph-content', 'figure'),
    Input('years-selection', 'value')
)
def update_graph(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)]
    fig = px.line(
        dff.groupby(['annee', 'mois'])['Valeur fonciere'].mean().reset_index(),
        x='mois',
        y='Valeur fonciere',
        color='annee',
        # title='Évolution de la moyenne de la valeur foncièce au cours de l\'année'
    )
    fig.update_layout(margin={'r': 0, 't': 24, 'l': 0, 'b': 0})
    fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.1, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    return fig


@callback(
    Output('graph-bar', 'figure'),
    Input('years-selection', 'value')
)
def update_bar_graph(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)]
    fig = px.histogram(
        dff.groupby(['Type local', 'annee'])['Valeur fonciere'].mean().reset_index(),
        x='Type local',
        y='Valeur fonciere',
        height=300,
        color='annee',
        barmode='group',
        # title='Title'
    )
    fig.update_layout(margin={'r': 0, 't': 24, 'l': 0, 'b': 0})
    fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.1, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    return fig


@callback(
    Output('graph-map', 'figure'),
    Input('scale-selection', 'value'),
    Input('years-selection', 'value')
)
def update_map(value, year):
    scale = echelle[value]
    years = inputTolist(year)
    dff = df[df['annee'].isin(years)].groupby(['annee', 'code_'+scale])['Valeur fonciere'].mean().reset_index()
    dff = dfScales[scale].merge(dff, how='left', left_on='code_'+scale, right_on='code_'+scale).fillna(0)
    fig = px.choropleth(dff, geojson=geojson[scale], featureidkey='properties.code', locations='code_'+scale, color='Valeur fonciere',
                        projection="mercator", color_continuous_scale=px.colors.sequential.Blues)
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(showlegend=False,
                        margin={"r":0,"t":0,"l":0,"b":0},
                    )
    return fig


@callback(
    Output('pie-chart-local', 'figure'),
    Input('years-selection', 'value')
)
def update_pie_local(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)].groupby(['annee', 'Type local'])['Valeur fonciere'].mean().reset_index()
    fig = px.pie(dff, values='Valeur fonciere', names='Type local', title='Proportion')
    # fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.02, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    fig.update_layout(showlegend=False)
    return fig


@callback(
    Output('pie-chart-mutation', 'figure'),
    Input('years-selection', 'value')
)
def update_pie_local(value):
    years = inputTolist(value)
    dff = df[df['annee'].isin(years)].groupby(['annee', 'Nature mutation'])['Valeur fonciere'].mean().reset_index()
    fig = px.pie(dff, values='Valeur fonciere', names='Nature mutation', title='Proportion')
    # fig.update_layout(legend={'orientation': 'h', 'yanchor': 'top', 'y': 1.02, 'xanchor': 'right', 'x': 1 , 'bgcolor': 'rgba(255,0,0,0)'})
    fig.update_layout(showlegend=False)
    return fig
