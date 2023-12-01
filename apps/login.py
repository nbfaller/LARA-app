import hashlib

from dash import callback_context, dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app
from apps import dbconnect as db

layout = html.Div(
    [
        dbc.Alert('Username or password is incorrect.', color = "danger", id = 'login_alert', is_open = False),
        dbc.Card(
            [
                dbc.CardHeader(html.H3('Log-in')),
                dbc.CardBody(
                    [
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Label("Username", width = 2),
                                        dbc.Col(
                                            dbc.Input(
                                                type = 'text',
                                                id = 'login_username',
                                                placeholder = 'Enter username'
                                            ), width = 5
                                        )
                                    ], className = 'mb-3'
                                ),
                                dbc.Row(
                                    [
                                        dbc.Label("Password", width = 2),
                                        dbc.Col(
                                            dbc.Input(
                                                type = 'password',
                                                id = 'login_password',
                                                placeholder = 'Enter password'
                                            ), width = 5
                                        )
                                    ], className = 'mb-3'
                                )
                            ]
                        ),
                        dbc.Button(
                            "Log-in", color = 'secondary', id = 'login_loginbtn'
                        )
                    ]
                )
            ],
            style = {
                'width' : '45vw',
                'position' : 'fixed',
                'top' : '50%',
                'left' : '50%',
                'transform' : 'translate(-50%, -50%)'
            }
        )
    ]
)

@app.callback(
    [
        Output('login_alert', 'is_open'),
        Output('currentuserid', 'data')
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
        openalert = False
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
    else: raise PreventUpdate

    if eventid == 'login_loginbtn':
        if loginbtn and username and password:
            sql = """SELECT user_id
            FROM userblock.RegisteredUser
            WHERE
                user_username = %s AND
                user_password = %s AND
                NOT userstatus_id = 4
            """

            encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()

            values = [username, encrypt_string(password)]
            cols = ['user_id']
            df = db.querydatafromdatabase(sql, values, cols)

            if df.shape[0]: currentuserid = df['user_id'][0]
            else:
                currentuserid = -1
                openalert = True
    elif eventid == 'sessionlogout' and pathname == '/logout':
        currentuserid = -1
    else: raise PreventUpdate
    return [openalert, currentuserid]

@app.callback(
    [Output('url', 'pathname')],
    [Input('currentuserid', 'modified_timestamp')],
    [State('currentuserid', 'data')]
)

def routelogin(logintime, user_id):
    ctx = callback_context
    if ctx.triggered:
        if user_id > 0:
            url = '/user/dashboard'
        else:
            url = '/'
    else: raise PreventUpdate
    return [url]