import dash
from dash import Dash, html, dcc
import dash_bootstrap_components as dbc

navBarStyle = {
    'display': 'flex',
    'justifyContent': 'space-between',
    'marginBottom': '16px',
    'background': 'white',
    'padding': '8px',
    'boxShadow': 'rgba(0, 0, 0, 0.15) 0px 3px 3px 0px',
    'position': 'sticky',
    'top': '0',
    'left': '0',
    'right': '0',
    'zIndex': '100',
}

filterStyle = {
    'display': 'flex',
    'alignItems': 'center',
    'gap': '8px'
}
dropdownStyle = {
    'width': '200px'
}

app = Dash(__name__, use_pages=True, assets_url_path='./dash/assets', external_stylesheets=[dbc.themes.BOOTSTRAP])
server=app.server
app.layout = html.Div([
    html.Div([
        html.H1('DashBoard', style={'margin': '0'}),
        html.Div([
            html.Div(
                dcc.Link(f"{page['name']}", href=page["relative_path"], style={'color': '#222', 'textDecoration': 'none', 'display': 'block', 'padding': '8px', 'border': '1px solid'})
            ) for page in dash.page_registry.values()
        ], style={'display':'flex'}),
    ], style=navBarStyle),
    dash.page_container 
])

if __name__ == '__main__':
    app.run(debug=True)
