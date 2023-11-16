from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('resource_classifications', 'children'),
        Output('resource_types', 'children')
    ],
    [Input('url', 'pathname')]
)

def home_loadclassifications(pathname):
    if pathname == '/' or pathname == '/home':
        sql1 = """SELECT * FROM resourceblock.SubjectTier1"""
        values1 = []
        cols1 = ['subj_tier1_ID', 'subj_tier1_name']
        df1 = db.querydatafromdatabase(sql1, values1, cols1)
        table1 = dbc.Table.from_dataframe(
            df1, striped = False, bordered = False, hover = True, size = 'sm',
            style = {
                #'border' : '0px'
            }
        )

        sql2 = """SELECT resourcetype_name FROM resourceblock.ResourceType"""
        values2 = []
        cols2 = ['resourcetype_name']
        df2 = db.querydatafromdatabase(sql2, values2, cols2)
        table2 = dbc.Table.from_dataframe(df2, striped = False, bordered = False, hover = True, size = 'sm')

        return [table1, table2]
    else:
        raise PreventUpdate

layout = html.Div(
    [
        html.Div(
            [
                html.Img(
                    src=app.get_asset_url('banner.jpg'),
                    style = {
                        'width' : '100vw',
                        'position' : 'relative',
                        'margin-left' : '-2em',
                        'margin-top' : '-5em',
                    }
                ),
                #html.H1(['Your books, now at the', html.Br(), 'reach of your fingertips'])
            ],
            id = 'banner'
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3('Browse by classification'),
                        html.Div(id = 'resource_classifications')
                    ]
                ),
                dbc.Col(
                    [
                        html.H3('Browse by resource type'),
                        html.Div(id = 'resource_types')
                    ]
                )
            ],
            style = {
                'margin-top' : '2em',
                'margin-left' : '5em',
                'margin-right' : '5em'
            }
        )
    ]
)