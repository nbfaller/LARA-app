from dash import dcc, html
import dash_bootstrap_components as dbc
import dash
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State
import os

from app import app
from apps import dbconnect as db

# ---------------------------------------- LOG-IN MODAL ----------------------------------------

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

# ---------------------------------------- SIDEBAR ----------------------------------------

sidebar = dbc.Col(
    [
        html.H6(['Main']), html.Hr(),
        html.A(['Dashboard'], href = '/user'), html.Br(),
        html.A(['Profile'], href = '/user/profile'), html.Br(), html.Br(),
        html.H6(['User Management']), html.Hr(),
        html.A(['Search User'], href = '/user/search'), html.Br(),
        html.A(['Register User'], href = '/user/profile?mode=register'), html.Br(),
        html.A(['User Removals'], href = '/user/removals'), html.Br(), html.Br(),
        html.H6(['Resources Management']), html.Hr(),
        html.A(['Search Resource'], href = '/resource/search'), html.Br(),
        html.A(['Catalog Resource'], href = '/resource/catalog'), html.Br(),
        html.A(['Resource Removals'], href = '/resource/removals')
    ], width = 2,
    style = {
        'margin-right' : '2em',
        'padding' : '1.5em',
    }
)

# ---------------------------------------- NAVBAR ----------------------------------------

# Callback for changing navbar content if logged in
@app.callback(
    [
        Output('navbar_links', 'children')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('currentuserid', 'data'),
        State('sessionlogout', 'data')
    ]
)

def navbarlinks(pathname, user_id, sessionlogout):
    if pathname:
        links = [
            dbc.Col(dbc.NavLink("🔎 Search", href = "/search"), width = 'auto'),
            dbc.Col(dbc.NavLink("🛒 Cart", href = "/cart"), width = 'auto'),
        ]
        if user_id == -1 and sessionlogout:
            links.append(
                dbc.Col(
                    dbc.NavLink("🔑 Log-in", id = 'navbar_login', href = "/login"),
                    width = 'auto'
                )
            )
        else:
            sql = """SELECT u.user_username AS username, u.user_lname AS lname, u.user_fname AS fname, u.user_mname AS mname,
                u.user_livedname AS livedname, u_t.usertype_name AS type
                FROM userblock.registereduser AS u
                LEFT JOIN utilities.usertype AS u_t ON u.usertype_id = u_t.usertype_id
                WHERE u.user_id = %s"""
            values = [user_id]
            cols = ['username', 'lname', 'fname', 'mname', 'livedname', 'type']
            df = db.querydatafromdatabase(sql, values, cols)
            fname = df['fname'][0]
            mname = ''
            if df['livedname'][0]: fname = df['livedname'][0]
            if df['mname'][0]: mname = df['mname'][0][0] + "."

            header = [
                dbc.Badge(
                    "%s • %s" % (df['type'][0], df['username'][0]),
                    color = 'primary',
                    className = 'mb-2'
                ),
                html.H4(
                    "%s %s %s" % (fname, mname, df['lname'][0]),
                    style = {
                        'color' : '#242424',
                        'line-height' : '0.7em'
                    }
                )
            ]

            image_path = "/assets/users/default.jpg"
            if os.path.exists("assets/users/%s-%s-%s.jpg" % (df['type'][0].lower(), user_id, df['username'][0])):
                image_path = "/assets/users/%s-%s-%s.jpg" % (df['type'][0].lower(), user_id, df['username'][0])

            if df['type'][0] == 'Student':
                sql = """SELECT us_c.college_name AS college, us_d.degree_name AS degree, us_y.year_level AS yearlevel
                    FROM userblock.userstudent AS us
                    LEFT JOIN utilities.college AS us_c ON us.student_college_id = us_c.college_id
                    LEFT JOIN utilities.degreeprogram AS us_d ON us.degree_id = us_d.degree_id AND us.student_college_id = us_d.college_id
                    LEFT JOIN utilities.yearlevel AS us_y ON us.year_id = us_y.year_id
                    WHERE us.student_id = %s"""
                values = [user_id]
                cols = ['college', 'degree', 'yearlevel']
                df = db.querydatafromdatabase(sql, values, cols)
                header.append(
                    html.Div(
                        [
                            html.Small("%s %s student" % (df['yearlevel'][0], df['degree'][0])),
                            html.Br(),
                            html.Small(df['college'][0])
                        ]
                    )
                )
            elif df['type'][0] == 'Faculty':
                sql = """SELECT uf_c.college_name AS college, uf.faculty_desig AS desig
                    FROM userblock.userfaculty AS uf
                    LEFT JOIN utilities.college AS uf_c ON uf.faculty_college_id = uf_c.college_id
                    WHERE uf.faculty_id = %s"""
                values = [user_id]
                cols = ['college', 'desig']
                df = db.querydatafromdatabase(sql, values, cols)
                header.append(
                    html.Div(
                        [
                            html.Small(df['desig'][0]),
                            html.Br(),
                            html.Small(df['college'][0])
                        ]
                    )
                )
            elif df['type'][0] == 'Staff':
                sql = """SELECT ut_o.office_name AS office, ut.staff_desig AS desig
                    FROM userblock.userstaff AS ut
                    LEFT JOIN utilities.office AS ut_o ON ut.office_id = ut_o.office_id
                    WHERE ut.staff_id = %s"""
                values = [user_id]
                cols = ['office', 'desig']
                df = db.querydatafromdatabase(sql, values, cols)
                header.append(
                    html.Div(
                        [
                            html.Small(df['desig'][0]),
                            html.Br(),
                            html.Small(df['office'][0])
                        ]
                    )
                )
            links.append(
                dbc.Col(
                    dbc.DropdownMenu(
                        [
                            dbc.DropdownMenuItem(
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            html.A(
                                                html.Img(
                                                    src = image_path,
                                                    className = "mb-3",
                                                    style = {
                                                        'border-radius' : '15px',
                                                        'height' : '64px'
                                                    }
                                                ),
                                                href = '/user/dashboard'
                                            ), width = 4
                                        ),
                                        dbc.Col(
                                            header,
                                            width = 12
                                        ),
                                    ]
                                ), header = True
                            ),
                            dbc.DropdownMenuItem(divider = True),
                            dbc.DropdownMenuItem("Dashboard", href = '/user/dashboard'),
                            dbc.DropdownMenuItem("Profile", href = '/user/profile'),
                            dbc.DropdownMenuItem("Change password", href = ''),
                            dbc.DropdownMenuItem("Log-out", href = '/logout', id = 'logout')
                        ],
                        label = html.B("👋 Hello, %s" % fname),
                        align_end = True,
                        in_navbar = True,
                        nav = True
                    ), width = 'auto'
                )
            )
        return [links]
    else: raise PreventUpdate

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
        html.Div(
            [
                dbc.Row(id = 'navbar_links')
                #dbc.NavLink("🔎 Search", href = "/search"),
                #dbc.NavLink("🛒 Cart", href = "/cart"),
                #dbc.NavLink("🔑 Log-in", id = 'navbar_login', href = "/login")
            ], style = {'margin-right' : '12px'}
        )
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

# ---------------------------------------- FOOTER ----------------------------------------

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
                    className = 'mb-3'
                ),
                dbc.Col(
                    [
                        html.H4(
                            ["LÁRA: Library Access & Resources Administration System"],
                            className = 'mb-1'
                        ),
                        "Copyright © 2024. University Library, Northwest Samar State University", html.Br(),
                        html.A("About LÁRA", href = "/about-us"), " • ", html.A("Main Website", href = "https://nwssu.edu.ph"), " • ", html.A("Frequently Asked Questions", href = "/faq"),
                    ],
                    width = "auto"
                ),
            ],
            style = {'margin' : 'auto'},
            align = 'center', justify = 'center'
        )
    ],
    style = {
        'margin-top' : '2em',
        'padding' : '2em 0em 2em 0em'
    }
)