import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_table
import dash
from dash.exceptions import PreventUpdate
import pandas as pd

from app import app

layout = html.Div(
    [
        html.Img(
            src=app.get_asset_url('banner.jpg'),
            style = {
                'width' : '100%',
                'margin-left' : '0em',
                'margin-right' : '0em'
            }
        ),
        html.Br(),
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
                                            placeholder = 'Search here'
                                        ),
                                        width = 7
                                    ),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'search_type',
                                            placeholder = 'Search by'
                                        ),
                                        width = 3
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
                        n_clicks = 0
                    ),
                    width = 3
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H3('Browse by classification')
                    ]
                ),
                dbc.Col(
                    [
                        html.H3('Browse by resource type')
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