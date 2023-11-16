from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate

from app import app

navlink_style = {
    'color' : '#f5f5f5'
}

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
        dbc.NavLink("🔎 SEARCH", href = "/search", style = navlink_style),
        dbc.NavLink("🛒 CART", href = "/cart", style = navlink_style),
        dbc.NavLink("LOG-IN", href = "/login", style = navlink_style)
    ],
    dark = True,
    color = 'dark',
    #style = {
    #    'background-image' : 'url(/assets/backgrounds/LARA-pattern-diagonal-green.png)',
    #    'background-size' : '3em 3em',
    #    'background-position' : '0 0',
    #    'background-repeat': 'repeat'
    #}
)

footer = html.Footer(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Img(
                            src=app.get_asset_url('nwssu-seal.png'),
                            style = {
                                'width' : '4em'
                            }
                        )
                    ], width = 1
                ),
                dbc.Col(
                    [
                        html.H4(["Library Access & Resources Administration System"]),
                        "Copyright © 2024. University Library, Northwest Samar State University",
                    ]
                ),
            ]
        )
    ],
    style = {
        'margin-top' : '2em',
        'margin-left' : '6em',
        'margin-right' : '6em',
        'padding' : '0em 0em 2em 2em'
    }
)