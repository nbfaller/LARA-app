from dash import dcc, html
import dash_bootstrap_components
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import webbrowser
from app import app

from apps import commonmodules as cm
from apps import home
from apps.user import user_dashboard as user_dash

# Layout definition
CONTENT_STYLE = {
    "margin-top" : "4em",
    "margin-left" : "1em",
    "margin-right" : "1em",
    "padding" : "1em 1em"
}

app.layout = html.Div(
    [
        dcc.Location(id = 'url', refresh = True),
        cm.navbar,
        html.Div(id = 'page-content', style = CONTENT_STYLE),
        cm.footer
    ]
)

@app.callback(
    [Output('page-content', 'children')],
    [Input('url', 'pathname')]
)

def displaypage(pathname):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'url':
            if pathname == '/' or pathname == '/home':
                returnlayout = home.layout
            elif pathname == '/search':
                returnlayout = "search"
            elif pathname == '/login':
                returnlayout = "login"
            elif pathname == '/about-us':
                returnlayout = "about us"
            elif pathname == '/faq':
                returnlayout = "faq"
            elif pathname == '/user' or pathname == '/user/dashboard':
                returnlayout = user_dash.layout
            else:
                returnlayout = 'error404'
            return [returnlayout]
        else:
            raise PreventUpdate
    else:
        raise PreventUpdate

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new = 0, autoraise = True)
    app.run_server(debug = False)