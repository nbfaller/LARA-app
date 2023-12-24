from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate

from app import app

login_modal = dbc.Modal(
    [
        dbc.ModalHeader(html.H3('Log-in')),
        dbc.ModalBody(
            dbc.Form(
                [
                    dbc.Row(
                        [
                            dbc.Label("Username", width = 1),
                            dbc.Col(
                                dbc.Input(
                                    type = 'text',
                                    id = 'login_username',
                                    placeholder = 'Enter username'
                                ), width = 5
                            )
                        ], className = 'mb-3'
                    ),
                    dbc.Row(
                        [
                            dbc.Label("Password", width = 1),
                            dbc.Col(
                                dbc.Input(
                                    type = 'password',
                                    id = 'login_password',
                                    placeholder = 'Enter password'
                                ), width = 5
                            )
                        ], className = 'mb-3'
                    )
                ]
            )
        ),
        dbc.ModalFooter(
            dbc.Button(
                "Log-in", color = 'secondary', id = 'login_loginbtn'
            )
        )
    ],
    centered = True,
    id = 'login_modal',
    backdrop = 'static'
)

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
        #'background-color' : '#f5f5f5',
        #'border-radius': '25px',
        #'border-style' : 'solid',
        #'border-width' : '1px',
        #'border-color' : '#ebe8e2',
        #'filter' : 'drop-shadow(0px 0px 15px #d3d0c9)',
        #'border-right' : '1px solid #ebe8e2',
        #'position' : 'sticky',
        'margin-right' : '2em',
        'padding' : '1.5em'
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
                                            src = app.get_asset_url('lara-wordmark.png'),
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
        dbc.NavLink("🔑 Log-in", id = 'navbar_login', href = "/login")
    ],
    dark = False,
    color = 'dark',
    style = {
        'background-image' : 'url(/assets/backgrounds/LARA-pattern-navbar.png)',
        'background-size' : '3em 3em',
        'background-position' : 'center top',
        'background-repeat': 'repeat',
        #'filter' : 'drop-shadow(0px 25px 35px #286052)',
        #'filter' : 'drop-shadow(0px 25px 35px #d3d0c9)',
        'z-index' : '1'
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
                    width = "auto"
                ),
                dbc.Col(
                    [
                        html.H4(["LÁRA: Library Access & Resources Administration System"]),
                        "Copyright © 2024. University Library, Northwest Samar State University", html.Br(),
                        html.A("About LÁRA", href = "/about-us"), " • ", html.A("Main Website", href = "https://nwssu.edu.ph"), " • ", html.A("Frequently Asked Questions", href = "/faq"),
                    ],
                    width = "auto"
                ),
            ],
            style = {
                'margin' : 'auto',
            },
            align = 'center', justify = 'center'
        )
    ],
    style = {
        'margin-top' : '2em',
        'padding' : '2em 0em 2em 0em'
    }
)