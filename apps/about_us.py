from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

layout = [
    html.Div(
        [
            dbc.Row(
                [
                    html.Img(
                        src = app.get_asset_url('logo/LARA-logo-500px-orig-green.png'),
                        style = {
                            'width' : '128px',
                            'padding-top' : '2em',
                            'padding-bottom' : '2em'
                        }
                    ),
                    html.Img(
                        src = app.get_asset_url('wordmark/LARA-wordmark-orange.png'),
                        style = {
                            'width' : '256px',
                            'padding-top' : '2em',
                            'padding-bottom' : '2em'
                        }
                    )
                ],
                style = {'margin-bottom' : '2em'},
                className = 'row justify-content-center'
            ),
            html.H4("""
                    LÁRA an ngaran san Library Access & Resources Administration System san Northwest Samar State University (NwSSU).
                    Ginlalára sini nga sistema an durodilain nga mga proseso san library sa uusa nga web-based information system.
                    Pinaagi san LÁRA, napadali na an pag-catalog, pagbibiling, ug paghuhuram san mga libro.
                """
            ), html.Br(),
            html.P(
                [
                    """LÁRA is the Library Access & Resources Administration System of the Northwest Samar State University (NwSSU).
                    It is based on """,
                    html.A(html.B("TUKLAS"), href = 'https://tuklas.up.edu.ph'),
                    """, the resource discovery tool of the University of the Philippines (which is itself based on VuFind, an
                    open-source software). Named after the Waray word for “weave,” LÁRA is designed to weave different library
                    processes together into a unified web-based information system. Book cataloging, searching, and borrowing
                    have never been easier."""
                ]
            ),
            html.P(
                """• • •""",
                style = {'text-align' : 'center'}
            ),
            html.H4("The Development Team"),
            html.P(
                [
                    "LÁRA is a project in IE 171 and 172 (Information Systems I and II) by BS Industrial Engineering students at the ",
                    html.A(html.B("Industrial Engineering and Operations Research Department (IEORD)"), href = 'https://ieor.engg.upd.edu.ph'),
                    " of the University of the Philippines College of Engineering in Diliman, Quezon City. The project team is composed of:"
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardImg(
                                        src="/assets/team/nics.jpg",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H4("Nicolas Bracamonte Faller, Jr."),
                                            html.P("""
                                                Nics is the team leader for this project. A native of Calbayog City, he is deeply passionate about
                                                universally accessible education, regional development, and student leadership. He has an acute
                                                addiction for UP Diliman kwek-kwek, Area 2 sisig, and white chocolate mocha frappucinos.
                                            """),
                                            html.A(
                                                html.Img(
                                                    src = app.get_asset_url('icons/linkedin.png'),
                                                    style = {
                                                        'width' : '32px',
                                                        #'filter' : 'invert(35%) sepia(91%) saturate(4733%) hue-rotate(153deg) brightness(93%) contrast(98%)'
                                                    }
                                                ),
                                                href = 'https://www.linkedin.com/in/nbfaller'
                                            )
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardImg(
                                        src="/assets/users/default.jpg",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H4("John Patrick Bonayon"),
                                            html.P("""
                                                Lorem ipsum dolor sit amet.
                                            """)
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardImg(
                                        src="/assets/users/default.jpg",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H4("Jon Michael Mollasgo"),
                                            html.P("""
                                                Lorem ipsum dolor sit amet.
                                            """)
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardImg(
                                        src="/assets/users/default.jpg",
                                    ),
                                    dbc.CardBody(
                                        [
                                            html.H4("Naomi Takagaki"),
                                            html.P("""
                                                Lorem ipsum dolor sit amet.
                                            """)
                                        ]
                                    )
                                ]
                            )
                        ]
                    )
                ],
                style = {
                    'padding-top' : '2em',
                    'padding-bottom' : '2em'
                }
            ),
            html.P(
                [
                    "This project was also made possible through the guidance and instruction of ",
                    html.A("Carlo Angelo Sonday", href = "https://ieor.engg.upd.edu.ph/people/faculty/assistant-professor/carlo-angelo-a-sonday/"),
                    " and ",
                    html.A("Pierre Allan Villena", href = "https://ieor.engg.upd.edu.ph/people/faculty/assistant-professor/pierre-allan-c-villena/"),
                    ", assistant professors at the UPD IEORD."
                ]
            ),
        ],
        style = {
            'padding-left' : '4em',
            'padding-right' : '4em'
        }
    )
]