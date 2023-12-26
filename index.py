from dash import dcc, html
import dash_bootstrap_components
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import webbrowser
from app import app

from apps import commonmodules as cm
from apps import home, login, about_us
from apps.user import user_dashboard, user_search, user_profile

# Layout definition
CONTENT_STYLE = {
    "margin-top" : "1em",
    "margin-left" : "1em",
    "margin-right" : "1em",
    "padding" : "1em 1em",
}

app.layout = html.Div(
    [
        html.Meta(
            name = "theme-color",
            content = '#286052'
        ),
        dcc.Location(id = 'url', refresh = True),
        # LOGIN DATA
        # 1) logout indicator, storage_type='session' means that data will be retained
        #  until browser/tab is closed (vs clearing data upon refresh)
        dcc.Store(id='sessionlogout', data=True, storage_type='session'),
        
        # 2) current_user_id -- stores user_id
        dcc.Store(id='currentuserid', data=-1, storage_type='session'),
        
        # 3) currentrole -- stores the role
        # we will not use them but if you have roles, you can use it
        dcc.Store(id='currentrole', data=-1, storage_type='session'),

        # Page mode and user id for viewing for those that have any
        dcc.Store(id = 'page_mode', storage_type = 'memory'),
        dcc.Store(id = 'view_id', storage_type = 'memory'),
        
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
                returnlayout = login.layout
            elif pathname == '/about-us':
                returnlayout = about_us.layout
            elif pathname == '/faq':
                returnlayout = "faq"
            elif pathname == '/user' or pathname == '/user/dashboard':
                returnlayout = user_dashboard.layout
            elif pathname == '/user/profile':
                returnlayout = user_profile.layout
            elif pathname == '/user/search':
                returnlayout = user_search.layout
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