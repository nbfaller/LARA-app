from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import os
import math

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('usertype_checklist', 'options'),
        Output('userstatus_checklist', 'options'),
        Output('borrowstatus_checklist', 'options'),
        Output('accesstype_checklist', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def populate_usertypedropdown (pathname):
    if pathname == '/user/search':
        sql = """SELECT usertype_name as label, usertype_id as value FROM utilities.usertype;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options1 = df.to_dict('records')

        sql = """SELECT userstatus_name as label, userstatus_id as value FROM utilities.userstatus;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options2 = df.to_dict('records')

        sql = """SELECT borrowstatus_name as label, borrowstatus_id as value FROM utilities.borrowstatus;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options3 = df.to_dict('records')

        sql = """SELECT accesstype_name as label, accesstype_id as value FROM utilities.accesstype;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        options4 = df.to_dict('records')

        return [options1, options2, options3, options4]
    else: raise PreventUpdate

# Callback for generating search results
@app.callback(
    [
        Output('search_results', 'children'),
        Output('usearch_pagination', 'max_value')
    ],
    [
        Input('url', 'pathname'),
        Input('search_input', 'value'),
        Input('usertype_checklist', 'value'),
        Input('userstatus_checklist', 'value'),
        Input('borrowstatus_checklist', 'value'),
        Input('accesstype_checklist', 'value'),
        Input('usearch_pagination', 'active_page')
    ]
)

def generate_results (pathname, input, usertype_filter, userstatus_filter, borrowstatus_filter, accesstype_filter, page):
    if pathname == '/user/search':
        sql = """SELECT u.user_id as id, u.user_username as username, u.user_lname as lname, u.user_fname as fname, u.user_mname as mname, u.user_livedname as livedname, u.user_pronouns as pronouns,
        t.usertype_name as usertype, b.borrowstatus_name as borrowstatus, s.userstatus_name as userstatus, a.accesstype_name as accesstype,
        us.degree_id as studentdegree, us.student_college_id as studentcollege, us.year_id as studentyear,
        uf.faculty_college_id as facultycollege, uf.faculty_desig as facultydesig,
        ut.office_id as staffoffice, ut.staff_desig as staffdesig
        FROM userblock.registereduser AS u
        INNER JOIN utilities.usertype AS t ON u.usertype_id = t.usertype_id
        INNER JOIN utilities.borrowstatus AS b ON u.borrowstatus_id = b.borrowstatus_id
        INNER JOIN utilities.userstatus AS s ON u.userstatus_id = s.userstatus_id
        INNER JOIN utilities.accesstype AS a ON u.accesstype_id = a.accesstype_id
        LEFT JOIN userblock.userstudent AS us ON u.user_id = us.student_id
        LEFT JOIN userblock.userfaculty AS uf ON u.user_id = uf.faculty_id
        LEFT JOIN userblock.userstaff AS ut ON u.user_id = ut.staff_id
        WHERE NOT u.userstatus_id = 4
        """

        values = []
        cols = [
            'id', 'username', 'lname', 'fname', 'mname', 'livedname', 'pronouns',
            'usertype', 'borrowstatus', 'userstatus', 'accesstype',
            'studentdegree', 'studentcollege', 'studentyear',
            'facultycollege', 'facultydesig',
            'staffoffice', 'staffdesig'
        ]

        if input:
            sql += "AND (u.user_lname ILIKE %s OR u.user_fname ILIKE %s OR u.user_livedname ILIKE %s OR u.user_mname ILIKE %s OR u.user_id ILIKE %s) "
            values += [f"%{input}%", f"%{input}%", f"%{input}%", f"%{input}%", f"%{input}%"]

        if usertype_filter:
            sql += "AND ("
            i = 0
            while i < len(usertype_filter):
                if i == 0:
                    sql += "u.usertype_id = %s "
                else:
                    sql += "OR u.usertype_id = %s "
                values += [int(f"{usertype_filter[i]}")]
                i += 1
            sql += ")"
        
        if userstatus_filter:
            sql += "AND ("
            i = 0
            while i < len(userstatus_filter):
                if i == 0:
                    sql += "u.userstatus_id = %s "
                else:
                    sql += "OR u.userstatus_id = %s "
                values += [int(f"{userstatus_filter[i]}")]
                i += 1
            sql += ")"
        
        if borrowstatus_filter:
            sql += "AND ("
            i = 0
            while i < len(borrowstatus_filter):
                if i == 0:
                    sql += "u.borrowstatus_id = %s "
                else:
                    sql += "OR u.borrowstatus_id = %s "
                values += [int(f"{borrowstatus_filter[i]}")]
                i += 1
            sql += ")"
        
        if accesstype_filter:
            sql += "AND ("
            i = 0
            while i < len(accesstype_filter):
                if i == 0:
                    sql += "u.accesstype_id = %s "
                else:
                    sql += "OR u.accesstype_id = %s "
                values += [int(f"{accesstype_filter[i]}")]
                i += 1
            sql += ")"

        sql += """ ORDER BY u.user_id;"""
        df = db.querydatafromdatabase(sql, values, cols)
        results = []
        max_value = math.ceil(len(df.index)/5)
        for i in df.index:
            if i >= (page-1)*5 and i < (page-1)*5+5:
                user_info = []
                if df['usertype'][i] == 'Student':
                    sql_utility = """SELECT us_d.degree_name AS degree, us_c.college_name AS college, us_y.year_level AS yearlevel
                    FROM userblock.userstudent as us
                    LEFT JOIN utilities.degreeprogram AS us_d ON (us.degree_id = us_d.degree_id AND us.student_college_id = us_d.college_id)
                    LEFT JOIN utilities.college AS us_c ON us.student_college_id = us_c.college_id
                    LEFT JOIN utilities.yearlevel AS us_y on us.year_id = us_y.year_id
                    WHERE student_id = %s;"""
                    values_utility = [df['id'][i]]
                    cols_utility = ['degree', 'college', 'yearlevel']
                    df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)

                    user_info = [
                        html.B([df_utility['yearlevel'][0].lower(), " student, ", df_utility['degree'][0]]), html.Br(),
                        df_utility['college'][0]
                    ]
                elif df['usertype'][i] == 'Faculty':
                    sql_utility = """SELECT uf_c.college_name AS college, uf.faculty_desig AS desig
                    FROM userblock.userfaculty AS uf
                    LEFT JOIN utilities.college AS uf_c ON uf.faculty_college_id = uf_c.college_id
                    WHERE faculty_id = %s;"""
                    values_utility = [df['id'][i]]
                    cols_utility = ['college', 'desig']
                    df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)

                    user_info = [
                        html.B(df_utility['desig'][0]), html.Br(),
                        df_utility['college'][0]
                    ]
                elif df['usertype'][i] == 'Staff':
                    sql_utility = """SELECT ut_o.office_name AS office, ut.staff_desig AS desig
                    FROM userblock.userstaff AS ut
                    LEFT JOIN utilities.office AS ut_o ON ut.office_id = ut_o.office_id
                    WHERE staff_id = %s;"""
                    values_utility = [df['id'][i]]
                    cols_utility = ['office', 'desig']
                    df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)

                    user_info = [
                        html.B(df_utility['desig'][0]), html.Br(),
                        df_utility['office'][0]
                    ]
                
                mname = ""
                if df['mname'][i]:
                    mname = str(df['mname'][i][0]).upper() + "."
                else: mname = ""

                name = ""
                if df['livedname'][i]: name = df['livedname'][i]
                else: name = df['fname'][i]

                pronouns = ""
                if df['pronouns'][i]:
                    user_info.append(html.Br())
                    user_info.append(
                        " (%s)" % df['pronouns'][i]
                    )
                
                image_path = "/assets/users/default.jpg"
                if os.path.exists("assets/users/%s-%s-%s.jpg" % (df['usertype'][i].lower(), df['id'][i], df['username'][i])):
                    image_path = "/assets/users/%s-%s-%s.jpg" % (df['usertype'][i].lower(), df['id'][i], df['username'][i])

                results.append(
                    dbc.Card(
                        [
                            dbc.Row(
                                [
                                    dbc.Col(
                                        html.A(
                                            dbc.CardImg(
                                                src = image_path,
                                                className="img-fluid rounded-start",
                                                style = {
                                                    'border-radius' : '15px',
                                                    #height' : '100%'
                                                }
                                            ),
                                            href = '/user/profile?mode=view&id=%s' % df['id'][i]
                                        ),
                                        style = {
                                            'maxWidth' : '256px',
                                        },
                                        className="col-md-4",
                                    ),
                                    dbc.Col(
                                        dbc.CardBody(
                                            [
                                                html.Small(
                                                    "%s • %s" % (df['usertype'][i], df['username'][i]),
                                                    className="card-text text-muted",
                                                ),
                                                html.A(
                                                    html.H4("%s, %s %s" % (df['lname'][i], name, mname), className = "card-title"),
                                                    href = '/user/profile?mode=view&id=%s' % df['id'][i]
                                                ),
                                                html.P(
                                                    user_info,
                                                    className="card-text",
                                                ),
                                                html.Small(
                                                    [
                                                        "User status: %s" % df['userstatus'][i], html.Br(),
                                                        "Borrowing status: %s" % df['borrowstatus'][i], html.Br(),
                                                        "Access type: %s" % df['accesstype'][i]
                                                    ],
                                                    className="card-text text-muted",
                                                ),
                                            ]
                                        ),
                                        className="col-md-8",
                                    )
                                ],
                                className="g-0 d-flex align-items-center",
                            )
                        ],
                        className = "mb-3",
                        style = {
                            #'maxWidth': '512px',
                            'border-radius' : '15px'
                        }
                    )
                )
        return [results, max_value]
    else:
        raise PreventUpdate

@app.callback(
    [
        Output('usertype_dropdown', 'color'),
        Output('usertype_dropdown', 'label'),
        Output('userstatus_dropdown', 'color'),
        Output('userstatus_dropdown', 'label'),
        Output('borrowstatus_dropdown', 'color'),
        Output('borrowstatus_dropdown', 'label'),
        Output('accesstype_dropdown', 'color'),
        Output('accesstype_dropdown', 'label'),
        Output('clearfilters_btn', 'color')
    ],
    [
        Input('url', 'pathname'),
        Input('usertype_checklist', 'value'),
        Input('userstatus_checklist', 'value'),
        Input('borrowstatus_checklist', 'value'),
        Input('accesstype_checklist', 'value')
    ]
)

def activate_dropdown(pathname, usertype, userstatus, borrowstatus, accesstype):
    if pathname == '/user/search':
        label_ut = ['User type']
        label_us = ['User status']
        label_bs = ['Borrowing status']
        label_at = ['Access type']
        color_ut = 'white'
        color_us = 'white'
        color_bs = 'white'
        color_at = 'white'
        color_clr = 'white'
        if not (usertype == None or usertype == []):
            label_ut += [
                " ",
                html.B(
                    len(usertype),
                    className = 'badge',
                    style = {
                        'background-color' : '#F5F5F5',
                        'color' : '#038b68'}
                )
            ]
            color_ut = 'primary'
            color_clr = 'warning'
        if not (userstatus == None or userstatus == []):
            label_us += [
                " ",
                html.B(
                    len(userstatus),
                    className = 'badge',
                    style = {
                        'background-color' : '#F5F5F5',
                        'color' : '#038b68'}
                )
            ]
            color_us = 'primary'
            color_clr = 'warning'
        if not (borrowstatus == None or borrowstatus == []):
            label_bs += [
                " ",
                html.B(
                    len(borrowstatus),
                    className = 'badge',
                    style = {
                        'background-color' : '#F5F5F5',
                        'color' : '#038b68'}
                )
            ]
            color_bs = 'primary'
            color_clr = 'warning'
        if not (accesstype == None or accesstype == []):
            label_at += [
                " ",
                html.B(
                    len(accesstype),
                    className = 'badge',
                    style = {
                        'background-color' : '#F5F5F5',
                        'color' : '#038b68'}
                )
            ]
            color_at = 'primary'
            color_clr = 'warning'
        return [color_ut, label_ut, color_us, label_us, color_bs, label_bs, color_at, label_at, color_clr]
    else: raise PreventUpdate

# Callback for clearing filters
@app.callback(
    [
        Output('usertype_checklist', 'value'),
        Output('userstatus_checklist', 'value'),
        Output('borrowstatus_checklist', 'value'),
        Output('accesstype_checklist', 'value')
    ],
    [
        Input('clearfilters_btn', 'n_clicks')
    ]
)

def clear_filters(btn):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'clearfilters_btn' and btn:
            return [[], [], [], []]
        else: raise PreventUpdate
    else: raise PreventUpdate

layout = html.Div(
    [
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.H1(['Search Users']),
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Input(
                                                id = 'search_input',
                                                type = 'text',
                                                placeholder = 'Search by last name, first name, middle name, lived name, or ID number',
                                            )
                                        )
                                    ],
                                    className = 'mb-3'
                                ),
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            "Filter by:",
                                            style = {
                                                'margin-top' : 'auto',
                                                'margin-bottom' : 'auto',
                                            },
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.DropdownMenu(
                                                    dbc.Checklist(
                                                        id = 'usertype_checklist',
                                                        style = {
                                                            'margin-left' : '1em',
                                                            'margin-right' : '1em'
                                                        }
                                                    ),
                                                    id = 'usertype_dropdown',
                                                    color = 'white',
                                                    label = 'User type',
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.DropdownMenu(
                                                    dbc.Checklist(
                                                        id = 'userstatus_checklist',
                                                        style = {
                                                            'margin-left' : '1em',
                                                            'margin-right' : '1em'
                                                        }
                                                    ),
                                                    id = 'userstatus_dropdown',
                                                    color = 'white',
                                                    label = 'User status',
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.DropdownMenu(
                                                    dbc.Checklist(
                                                        id = 'borrowstatus_checklist',
                                                        style = {
                                                            'margin-left' : '1em',
                                                            'margin-right' : '1em'
                                                        }
                                                    ),
                                                    id = 'borrowstatus_dropdown',
                                                    color = 'white',
                                                    label = 'Borrowing status',
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.DropdownMenu(
                                                    dbc.Checklist(
                                                        id = 'accesstype_checklist',
                                                        style = {
                                                            'margin-left' : '1em',
                                                            'margin-right' : '1em'
                                                        }
                                                    ),
                                                    id = 'accesstype_dropdown',
                                                    color = 'white',
                                                    label = 'Access type',
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    '🆇 Clear filters',
                                                    id = 'clearfilters_btn',
                                                    color = 'white',
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        ),
                                        dbc.Col(
                                            [
                                                dbc.Button(
                                                    'Recommend deactivation',
                                                    color = 'danger',
                                                    id = 'deactivate_btn',
                                                    style = {
                                                        'margin-left' : 'auto',
                                                        'margin-right' : '0'
                                                    },
                                                    size = 'sm'
                                                )
                                            ],
                                            width = 'auto'
                                        )
                                    ],
                                    className = 'mb-3'
                                ),
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            id = 'search_results'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Pagination(
                                    id = 'usearch_pagination',
                                    first_last = True,
                                    previous_next = True,
                                    max_value = 1,
                                    active_page = 1,
                                    #style = {'margin' : 'auto'}
                                ),
                            ),
                        )
                    ]
                )
            ]
        )
    ]
)