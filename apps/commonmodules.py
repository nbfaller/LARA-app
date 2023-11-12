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
        html.A(
            dbc.Row(
                [
                    dbc.Col(dbc.NavbarBrand("LÁRA", className = "ms-2"))
                ],
                align = "center",
                className = 'g-0'
            ),
            href = "/home"
        ),
        dbc.NavLink("SEARCH", href = "/search", style = navlink_style),
        dbc.NavLink("CART", href = "/cart", style = navlink_style),
        dbc.NavLink("LOG-IN", href = "/login", style = navlink_style)
    ],
    dark = True,
    color = 'dark'
)