from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy
from urllib.parse import urlparse, parse_qs

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('basic_info', 'children')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)

def show_profile(pathname, search):
    if pathname == '/user/profile':
        parsed = urlparse(search)
        user_id = parse_qs(parsed.query)['id'][0]
        sql = """SELECT user_lname as lname, user_fname as fname, user_mname as mname, usertype_id as type, user_username as username
        FROM userblock.registereduser WHERE user_id = '%s';
        """ % user_id
        values = []
        cols = ['lname', 'fname', 'mname', 'type', 'username']
        df = db.querydatafromdatabase(sql, values, cols)

        sql_utility = """SELECT usertype_name as type FROM userblock.usertype WHERE usertype_id = '%s';""" % df['type'][0]
        values_utility = []
        cols_utility = ['type']
        df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
        type = df_utility['type'][0]

        if df['mname'][0] == None:
            df.loc[0, 'mname'] = str('')

        basic_info = [
            html.P(
                [
                    '%s • %s' % (type, df['username'][0])
                ], className = 'badge'
            ),
            html.H1("%s, %s %s" % (df['lname'][0], df['fname'][0], df['mname'][0]))
        ]

        return [basic_info]
    else: raise PreventUpdate

layout = [
    dbc.Row(
        [
            cm.sidebar,
            dbc.Col(
                [
                    html.Div(id = 'basic_info')
                ]
            )
        ]
    )
]