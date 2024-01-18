from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
import pytz

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

layout = html.Div(
    [
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                html.H1("Active wishlists"),
                                html.Hr()
                            ]
                        )
                    ]
                )
            ]
        )
    ]
)