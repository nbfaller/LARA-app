from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate

from app import app

sidebar = dbc.Col(
    [
        html.H6(['Main']), html.Hr(),
        html.A(['Dashboard'], href = '/user'), html.Br(),
        html.A(['Profile'], href = '/user/profile'), html.Br(), html.Br(),
        html.H6(['User Management']), html.Hr(),
        html.A(['Search User'], href = '/user/search'), html.Br(),
        html.A(['Register User'], href = '/user/register'), html.Br()
    ], width = 2,
    style = {
        #'background-color' : '#ebe8e2',
        #'border-radius': '25px',
        'margin-right' : '2em',
        #'padding' : '1.5em'
    }
)

navlink_color = 'body'
navbar = dbc.Navbar(
    [
        dbc.Col(
            [
                html.A(
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.NavbarBrand(
                                    [
                                        html.Img(
                                            src=app.get_asset_url('lara-wordmark.png'),
                                            style = {'height' : '2em'}
                                        )
                                    ]
                                    , className = "ms-2"
                                )
                            )
                        ],
                        align = "center",
                        className = 'g-0'
                    ),
                    href = "/home"
                )
            ]
        ),
        dbc.NavLink("🔎 Search", href = "/search"),
        dbc.NavLink("🛒 Cart", href = "/cart"),
        dbc.NavLink("Log-in", href = "/login")
    ],
    dark = False,
    color = 'dark',
    style = {
        'background-image' : 'url(/assets/backgrounds/LARA-pattern-navbar.png)',
        'background-size' : '3em 3em',
        'background-position' : 'center',
        'background-repeat': 'repeat',
        #'filter' : 'drop-shadow(0px 25px 35px #286052)',
        'z-index' : '5'
    },
)

footer = html.Footer(
    [
        dbc.Row(
            [
                #html.Hr(),
                dbc.Col(
                    [
                        html.A(
                            html.Img(
                                src = app.get_asset_url('nwssu-seal.png'),
                                style = {
                                    'width' : '6em'
                                }
                            ),
                            href = "https://nwssu.edu.ph"
                        )
                    ],
                    width = "auto",
                    style = {
                        #'background-color' : '#000'
                    },
                ),
                dbc.Col(
                    [
                        html.H4(["LÁRA: Library Access & Resources Administration System"]),
                        "Copyright © 2024. University Library, Northwest Samar State University", html.Br(),
                        html.A("About LÁRA", href = "about-us"), " • ", html.A("Main Website", href = "https://nwssu.edu.ph"), " • ", html.A("Frequently Asked Questions", href = "faq"),
                    ],
                    width = "auto",
                    style = {
                        #'background-color' : '#000'
                    },
                ),
            ],
            style = {
                'margin-top' : '2em',
                #'margin-left' : '10em',
                #'margin-right' : '10em',
                'padding' : '0em 0em 2em 0em'
                #'background-color' : '#000'
            },
            align = "center", justify = "center"
        )
    ],
    style = {
        #'background-image' : 'linear-gradient(rgba(235,232,226,0), rgba(235,232,226,1))'
    }
)