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
        Output('search_type', 'options'),
        Output('resource_classifications', 'children'),
        Output('resource_types', 'children')
    ],
    [
        Input('url', 'pathname')
    ]
)

def search_populatetypes(pathname):
    if pathname == '/' or pathname == '/home':
        sql = """
        SELECT searchtype_desc as label, searchtype_id as value
        FROM utilities.searchtype;
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        
        search_options = df.to_dict('records')

        sql = """SELECT CONCAT(TO_CHAR(subj_tier1_id*100, '000'), ' ', subj_tier1_name) as label, subj_tier1_ID as value FROM utilities.SubjectTier1"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        list1 = []
        for i in df.index:
            list1.append(
                html.A(
                    [
                        str(df.iloc[i]['label']),
                        html.Br()
                    ],
                    href = '/search?subj_tier1_id=' + str(df.iloc[i]['value'])
                )
            )

        sql = """SELECT resourcetype_name as label, resourcetype_ID as value FROM utilities.ResourceType"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        list2 = []
        for i in df.index:
            list2.append(
                html.A(
                    [
                        str(df.iloc[i]['label']),
                        html.Br()
                    ],
                    href = '/search?resourcetype_id=' + str(df.iloc[i]['value'])
                )
            )

        return [search_options, list1, list2]
    else:
        raise PreventUpdate

layout = html.Div(
    [
        html.Div(
            [
                html.H1(
                    [
                        html.Span(
                            """Your books, now at the reach of your fingertips.""",
                            style = {
                                #'color' : '#f5f5f5',
                                'background-color' : '#f49c13'
                            }
                        )
                    ],
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
                        'width' : '100%',
                        'object-fit' : 'cover',
                        'z-index' : '-1',
                        'mask-image' : 'linear-gradient(to bottom, rgba(0, 0, 0, 1.0) 50%, transparent 100%)'
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
        dbc.Form(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Input(
                                type = 'text',
                                id = 'search_input',
                                placeholder = "Search here"
                            ),
                            width = 7,
                            className = 'mb-3',
                            style = {'min-width' : '400px'}
                        ),
                        dbc.Col(
                            dcc.Dropdown(
                                id = 'search_type',
                                placeholder = "Search by"
                            ),
                            width = 3,
                            className = 'mb-3',
                            style = {'min-width' : '150px'}
                        ),
                        dbc.Col(
                            dbc.Button(
                                '🔎 Search',
                                id = 'search_submit',
                                n_clicks = 0,
                                style = {'width' : '100%'}
                            ),
                            width = 2,
                            className = 'mb-3',
                            style = {'min-width' : '150px'}
                        ),
                    ],
                    align = 'center',
                    justify = 'center'
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
                'margin-left' : '15em',
                'margin-right' : '15em',
                #'align-content' : 'center'
            },
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3('Browse by classification'),
                        html.Div(id = 'resource_classifications')
                    ],
                    width = "auto",
                    className = 'mb-3',
                    #style = {'max-width' : '400px'}
                ),
                dbc.Col(
                    [
                        html.H3('Browse by resource type'),
                        html.Div(id = 'resource_types')
                    ],
                    width = "auto",
                    className = 'mb-3',
                    #style = {'max-width' : '400px'}
                )
            ],
            align = "center",
            justify = "center",
            style = {
                'margin-top' : '3em',
                #'padding-top' : '-1em'
            }
        )
    ]
)