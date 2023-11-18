from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
#import dash_ag_grid as dag

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
                html.H1(
                    ["Your books, now at the", html.Br(),"reach of your fingertips"],
                    style = {
                        'position' : 'absolute',
                        'margin-top' : '6em',
                        'margin-left' : '1em',
                        'z-index' : '2',
                        'color' : '#f5f5f5'
                    }
                ),
                html.Img(
                    src=app.get_asset_url('banner.jpg'),
                    style = {
                        'width' : '100vw', # causes picture to stretch instead of crop (maybe set height as fixed instead)
                        'position' : 'relative',
                        'margin-left' : '-2em',
                        'margin-top' : '-5em',
                        'filter' : 'drop-shadow(0px 25px 35px #d3d0c9)',
                        'z-index' : '1'
                    }
                ),
                #html.H1(['Your books, now at the', html.Br(), 'reach of your fingertips'])
            ],
            id = 'banner'
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Form(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'search_input',
                                            placeholder = "Search here"
                                        ), width = 9
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'search_type',
                                            placeholder = "Search by"
                                        )
                                    )
                                ]
                            )
                        ]
                    )
                ),
                dbc.Col(
                    dbc.Button(
                        '🔎 Search',
                        id = 'search_submit',
                        n_clicks = 0,
                        style = {'width' : '100%'}
                    ),
                    width = 2
                ),
                #dbc.Col(
                #    "Advanced search",
                #    width = 2
                #)
            ],
            style = {
                'position' : 'relative',
                'z-index' : '2',
                'margin-top' : '3em',
                'margin-left' : '10em',
                'margin-right' : '10em'
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3('Browse by classification'),
                        html.Div(id = 'resource_classifications')
                    ], width = "auto"
                ),
                dbc.Col(
                    [
                        html.H3('Browse by resource type'),
                        html.Div(id = 'resource_types')
                    ], width = "auto"
                )
            ], align = "center", justify = "center",
            style = {
                'margin-top' : '3em',
                #'margin-left' : '10em',
                #'margin-right' : '10em'
            }
        )
    ]
)