import hashlib

import dash
from dash import callback_context, dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('login_alert', 'is_open'),
        Output('currentuserid', 'data'),
        Output('currentrole', 'data')
    ],
    [
        Input('login_loginbtn', 'n_clicks'),
        Input('sessionlogout', 'modified_timestamp')
    ],
    [
        State('login_username', 'value'),
        State('login_password', 'value'),
        State('sessionlogout', 'data'),
        State('currentuserid', 'data'),
        State('url', 'pathname')
    ]
)

def loginprocess(loginbtn, sessionlogout_time,
                 username, password, sessionlogout,
                 currentuserid, pathname):
    ctx = callback_context
    if ctx.triggered:
        accesstype = 0
        openalert = False
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'login_loginbtn':
            if loginbtn and username and password:
                sql = """SELECT user_id, accesstype_id
                FROM userblock.RegisteredUser
                WHERE
                    user_username = %s AND
                    user_password = %s AND
                    NOT userstatus_id = 4
                """
                encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
                values = [username, encrypt_string(password)]
                cols = ['user_id', 'accesstype_id']
                df = db.querydatafromdatabase(sql, values, cols)
                if df.shape[0]:
                    currentuserid = df['user_id'][0]
                    accesstype = df['accesstype_id'][0]
                else:
                    currentuserid = -1
                    openalert = True
        elif eventid == 'sessionlogout' and pathname == '/logout':
            currentuserid = -1
        else: raise PreventUpdate
        return [openalert, currentuserid, accesstype]
    else: raise PreventUpdate

@app.callback(
    [
        Output('url', 'pathname')
    ],
    [
        Input('currentuserid', 'modified_timestamp')
    ],
    [
        State('currentuserid', 'data'),
        State('url', 'pathname')
    ]
)

def routelogin(logintime, user_id, pathname):
    ctx = dash.callback_context
    if ctx.triggered:
        if pathname == '/login':
            if user_id != -1:
                url = '/user/dashboard'
            else:
                url = '/'
        else: raise PreventUpdate
    else: raise PreventUpdate
    return [url]

layout = html.Div(
    [
        dbc.Card(
            [
                dbc.CardHeader(
                    html.H3('Log-in'),
                    style = {'text-align' : 'center'}
                ),
                dbc.CardBody(
                    [
                        dbc.Row(
                            html.Img(
                                src=app.get_asset_url('logo/LARA-logo-500px-orig-green.png'),
                                style = {
                                    'height' : '35%',
                                    'width' : '35%',
                                    'margin' : 'auto',
                                }
                            ),
                            style = {
                                'margin-top' : '1em',
                                'margin-bottom' : '2em'
                            }
                        ),
                        dbc.Form(
                            [
                                dbc.Alert(
                                    'Username or password is incorrect',
                                    color = 'danger',
                                    id = 'login_alert',
                                    is_open = False
                                ),
                                dbc.Row(
                                    [
                                        #dbc.Label("Username", width = 3),
                                        dbc.Col(
                                            dbc.Input(
                                                type = 'text',
                                                id = 'login_username',
                                                placeholder = 'Username'
                                            )#, width = 7
                                        )
                                    ], className = 'mb-3'
                                ),
                                dbc.Row(
                                    [
                                        #dbc.Label("Password", width = 3),
                                        dbc.Col(
                                            dbc.Input(
                                                type = 'password',
                                                id = 'login_password',
                                                placeholder = 'Password'
                                            )#, width = 7
                                        )
                                    ], className = 'mb-3'
                                )
                            ], className = 'align-self-center'
                        ),
                        dbc.Row(
                            dbc.Button(
                                "Log-in",
                                color = 'primary',
                                id = 'login_loginbtn'
                            ),
                            style = {
                                'margin' : 'auto'
                            }
                        )
                    ]
                )
            ],
            style = {
                'width' : '400px',
                'margin' : 'auto',
                'position' : 'relative',
                'top' : '2em'
            }
        )
    ]
)