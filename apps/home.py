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
        [Output('search_type', 'options')],
        [Input('url', 'pathname')]
)

def search_populatetypes(pathname):
    if pathname == '/' or pathname == '/home':
        sql = """
        SELECT searchtype_desc as label, searchtype_id as value
        FROM utilities.searchtype;
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        search_options = df.to_dict('records')
        return [search_options]
    
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('resource_classifications', 'children'),
        Output('resource_types', 'children')
    ],
    [Input('url', 'pathname')]
)

def home_loadclassifications(pathname):
    if pathname == '/' or pathname == '/home':
        sql1 = """SELECT subj_tier1_name as label, subj_tier1_ID as value FROM utilities.SubjectTier1"""
        values1 = []
        cols1 = ['label', 'value']
        df1 = db.querydatafromdatabase(sql1, values1, cols1)
        list1 = []
        for i in df1.index:
            list1.append(
                html.A(
                    [
                        str(df1.iloc[i]['label']),
                        html.Br()
                    ],
                    href = '/search?subj_tier1_id=' + str(df1.iloc[i]['value'])
                )
            )

        sql2 = """SELECT resourcetype_name as label, resourcetype_ID as value FROM utilities.ResourceType"""
        values2 = []
        cols2 = ['label', 'value']
        df2 = db.querydatafromdatabase(sql2, values2, cols2)
        list2 = []
        for i in df2.index:
            list2.append(
                html.A(
                    [
                        str(df2.iloc[i]['label']),
                        html.Br()
                    ],
                    href = '/search?resourcetype_id=' + str(df2.iloc[i]['value'])
                )
            )

        return [list1, list2]
    else:
        raise PreventUpdate

layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    ["""Your books, now at the reach of your fingertips."""],
                    style = {
                        'max-width' : '16em',
                        #'font-size' : '40px',
                        'position' : 'absolute',
                        'bottom' : '2em',
                        'padding-left' : '2em',
                        'padding-right' : '2em',
                        'z-index' : '2',
                        'color' : '#f5f5f5',
                    }
                ),
                html.Img(
                    src=app.get_asset_url('banner.jpg'),
                    style = {
                        'height' : '30em',
                        'z-index' : '-1'
                    }
                ),
            ],
            id = 'banner',
            style = {
                'position' : 'relative',
                'margin-left' : '-2em',
                'margin-top' : '-2em',
                'width' : '100vw',
                'overflow' : 'hidden'
            }
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
                #'padding-top' : '-1em'
            }
        )
    ]
)