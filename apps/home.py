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
                        'width' : '100%',
                        'margin-bottom' : '1em'
                    }
                )
            ],
            id = 'banner'
        ),
        html.Div(
            [
                dbc.Row(
                    [
                        html.Div(
                            dbc.Form(
                                [
                                    dbc.Row(
                                        [
                                            html.Div(
                                                dbc.Input(
                                                    type = 'text',
                                                    id = 'search_input',
                                                    placeholder = "Search here"
                                                ), style = {'width' : '70%'}
                                            ),
                                            html.Div(
                                                dcc.Dropdown(
                                                    id = 'search_type',
                                                    placeholder = "Search by"
                                                ), style = {'width' : '30%'}
                                            ),
                                        ]
                                    )
                                ]
                            ), style = {'width' : '60%'}
                        ),
                        dbc.Button(
                            '🔎 Search',
                            id = 'search_submit',
                            n_clicks = 0
                        )
                    ], justify = "center"
                )
            ]
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