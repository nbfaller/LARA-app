from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import webbrowser
from urllib.parse import urlparse, parse_qs

from app import app
from apps import commonmodules as cm
from apps import home, login, about_us, faq
from apps.user import user_dashboard, user_search, user_profile, user_removals
from apps.resource import resource_search, resource_catalog, resource_record, resource_removals
from apps.circulation import circulation_loans, circulation_wishlists

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
        dcc.Store(id='sessionlogout', data = True, storage_type='local'),
        
        # 2) current_user_id -- stores user_id
        dcc.Store(id='currentuserid', data = -1, storage_type='local'),
        
        # 3) currentrole -- stores the role
        # we will not use them but if you have roles, you can use it
        dcc.Store(id='currentrole', data = 0, storage_type='local'),

        # Page mode and user id for viewing for those that have any
        dcc.Store(id = 'page_mode', data = -1, storage_type = 'memory'),
        dcc.Store(id = 'view_id', data = -1, storage_type = 'memory'),
        #dcc.Store(id = 'current_page', data = 1, storage_type = 'memory'),
        
        cm.navbar,
        html.Div(id = 'page-content', style = CONTENT_STYLE),
        cm.footer
    ]
)

@app.callback(
    [
        Output('page-content', 'children'),
        Output('sessionlogout', 'data'),
        #Output('currentuserid', 'data'),
        #Output('currentrole', 'data')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
        State('currentrole', 'data'),
        State('url', 'search')
    ]
)

def displaypage(pathname, sessionlogout, user_id, accesstype, search):
    mode = None
    parsed = urlparse(search)
    if parse_qs(parsed.query):
        mode = parse_qs(parsed.query)['mode'][0]
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'url':
            if pathname == '/' or pathname == '/home' or pathname == '/logout':
                returnlayout = home.layout
            elif pathname == '/search' or pathname == '/resource/search':
                returnlayout = resource_search.layout
            elif pathname == '/resource/record':
                returnlayout = resource_record.layout
            elif pathname == '/about-us':
                returnlayout = about_us.layout
            elif pathname == '/faq':
                returnlayout = faq.py
            elif pathname == '/login':
                returnlayout = login.layout
            elif user_id != -1:
                if accesstype >= 1:
                    if pathname == '/user' or pathname == '/user/dashboard':
                        returnlayout = user_dashboard.layout
                    elif pathname == '/user/profile' and mode != 'register':
                        returnlayout = user_profile.layout
                    else:
                        returnlayout = 'Error 404: Request not found'
                elif accesstype == 2:
                    if pathname == '/user/search':
                        returnlayout = user_search.layout
                    elif pathname == '/resource/catalog':
                        returnlayout = resource_catalog.layout
                    elif pathname == '/circulation/loans':
                        returnlayout = circulation_loans.layout
                    elif pathname == '/circulation/wishlists':
                        returnlayout = circulation_wishlists.layout
                    else:
                        returnlayout = 'Error 403: Forbidden'
                elif accesstype == 3 or accesstype == 5:
                    if pathname == '/user/removals':
                        returnlayout = user_removals.layout
                    else:
                        returnlayout = 'Error 403: Forbidden'
                elif accesstype == 4:
                    if pathname == '/resource/removals':
                        returnlayout = resource_removals.layout
                    else:
                        returnlayout = 'Error 403: Forbidden'
                else:
                    returnlayout = 'Error 403: Forbidden'
            else:
                returnlayout = 'Error 404: Request not found'
            # decide sessionlogout value
            logout_conditions = [
                pathname in ['/', '/logout'],
                user_id == -1,
                not user_id
            ]
            sessionlogout = any(logout_conditions)
        else:
            raise PreventUpdate
        return [returnlayout, sessionlogout,
                #user_id, accesstype
            ]
    else:
        raise PreventUpdate

if __name__ == '__main__':
    webbrowser.open('http://127.0.0.1:8050/', new = 0, autoraise = True)
    app.run_server(debug = False)