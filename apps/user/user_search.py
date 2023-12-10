from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('search_results', 'children')
    ],
    [
        Input('url', 'pathname'),
        #Input('search_input', 'value')
    ]
)

def generate_results (pathname):
    if pathname == '/user/search':
        sql = """SELECT user_id as id, user_username as username, user_lname as lname, user_fname as fname, user_mname as mname,
        borrowstatus_id as borrowstatus, userstatus_id as userstatus, accesstype_id as accesstype, usertype_id as usertype FROM userblock.registereduser;
        """
        values = []
        cols = ['id', 'username', 'lname', 'fname', 'mname', 'borrowstatus', 'userstatus', 'accesstype', 'usertype']
        df = db.querydatafromdatabase(sql, values, cols)
        
        college = ""
        degree = ""
        year_level = ""
        faculty_desig = ""
        office = ""
        staff_desig = ""
        results = []

        for i in df.index:
            # Utility queries
            sql_utility = """SELECT userstatus_name FROM userblock.userstatus WHERE userstatus_id = %s;""" % df['userstatus'][i]
            values_utility = []
            cols_utility = ['userstatus_name']
            df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
            userstatus_name = df_utility.iloc[0,0]

            sql_utility = """SELECT borrowstatus_name FROM userblock.borrowstatus WHERE borrowstatus_id = %s;""" % df['borrowstatus'][i]
            values_utility = []
            cols_utility = ['borrowstatus_name']
            df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
            borrowstatus_name = df_utility.iloc[0,0]

            sql_utility = """SELECT accesstype_name FROM userblock.accesstype WHERE accesstype_id = %s;""" % df['accesstype'][i]
            values_utility = []
            cols_utility = ['accesstype_name']
            df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
            accesstype_name = df_utility.iloc[0,0]

            sql_utility = """SELECT usertype_name FROM userblock.usertype WHERE usertype_id = %s;""" % df['usertype'][i]
            values_utility = []
            cols_utility = ['usertype_name']
            df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
            usertype_name = df_utility.iloc[0,0]

            user_info = []

            if df['usertype'][i] == 1:
                sql_student = """SELECT degree_id as degree, student_college_id as college, year_id as year_level FROM userblock.userstudent
                WHERE student_id = '%s';""" % df['id'][i]
                values_student = []
                cols_student = ['degree', 'college', 'year_level']
                df_student = db.querydatafromdatabase(sql_student, values_student, cols_student)
                college = df_student['college'][0]
                degree = df_student['degree'][0]
                year_level = df_student['year_level'][0]

                sql_utility = """SELECT year_level FROM userblock.yearlevel WHERE year_id = %s;""" % year_level
                values_utility = []
                cols_utility = ['year_level']
                df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
                year_level = df_utility['year_level'][0]

                sql_utility = """SELECT degree_name FROM userblock.degreeprogram WHERE degree_id = %s AND college_id = %s;""" % (degree, college)
                values_utility = []
                cols_utility = ['degree_name']
                df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
                degree = df_utility['degree_name'][0]

                sql_utility = """SELECT college_name FROM userblock.college WHERE college_id = %s;""" % college
                values_utility = []
                cols_utility = ['college_name']
                df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
                college = df_utility['college_name'][0]

                user_info = [
                    html.B([year_level.lower(), " student, ", degree]), html.Br(),
                    college
                ]
            elif df['usertype'][i] == 2:
                sql_faculty = """SELECT faculty_college_id as college, faculty_desig FROM userblock.userfaculty
                WHERE faculty_id = '%s';""" % df['id'][i]
                values_faculty = []
                cols_faculty = ['college', 'faculty_desig']
                df_faculty = db.querydatafromdatabase(sql_faculty, values_faculty, cols_faculty)
                college = df_faculty['college'][0]
                faculty_desig = df_faculty['faculty_desig'][0]

                sql_utility = """SELECT college_name FROM userblock.college WHERE college_id = %s;""" % college
                values_utility = []
                cols_utility = ['college_name']
                df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
                college = df_utility['college_name'][0]

                user_info = [
                    html.B(faculty_desig), html.Br(),
                    college
                ]
            elif df['usertype'][i] == 3:
                sql_staff = """SELECT office_id as office, staff_desig FROM userblock.userstaff
                WHERE staff_id = '%s';""" % df['id'][i]
                values_staff = []
                cols_staff = ['office', 'staff_desig']
                df_staff = db.querydatafromdatabase(sql_staff, values_staff, cols_staff)
                office = df_staff['office'][0]
                staff_desig = df_staff['staff_desig'][0]

                sql_utility = """SELECT office_name FROM userblock.office WHERE office_id = %s;""" % office
                values_utility = []
                cols_utility = ['office_name']
                df_utility = db.querydatafromdatabase(sql_utility, values_utility, cols_utility)
                office = df_utility['office_name'][0]

                user_info = [
                    html.B(staff_desig), html.Br(),
                    office
                ]

            if df['mname'][i]:
                df.loc[i,'mname'] = str(df['mname'][i][0]).upper() + "."
            else: df.loc[i,'mname'] = ""

            results.append(
                dbc.Card(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.A(
                                        dbc.CardImg(
                                            src="/assets/users/%s-%s-%s.jpg" % (usertype_name.lower(), df['id'][i], df['username'][i]),
                                            className="img-fluid rounded-start",
                                            style = {
                                                'border-radius' : '15px',
                                                #height' : '100%'
                                            }
                                        ),
                                        href = '/user/profile/%s' % df['id'][i]
                                    ),
                                    style = {
                                        'maxWidth' : '256px',
                                        #'height' : '100%'
                                    },
                                    className="col-md-4",
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            html.Small(
                                                "%s • %s" % (usertype_name, df['username'][i]),
                                                className="card-text text-muted",
                                            ),
                                            html.A(
                                                html.H4("%s, %s %s" % (df['lname'][i], df['fname'][i], df['mname'][i]), className = "card-title"),
                                                href = '/user/profile/%s' % df['id'][i]
                                            ),
                                            html.P(
                                                user_info,
                                                className="card-text",
                                            ),
                                            html.Small(
                                                [
                                                    "User status: %s" % userstatus_name, html.Br(),
                                                    "Borrowing status: %s" % borrowstatus_name, html.Br(),
                                                    "Access type: %s" % accesstype_name
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
        
        return [results]
    else:
        raise PreventUpdate

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
                                                placeholder = 'Search here',
                                            ), width = 6
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id = 'search_type',
                                                placeholder = 'Search by',
                                            ), width = 3
                                        )
                                    ],
                                    className = 'mb-3'
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(
                            id = 'search_results'
                        )
                    ]
                )
            ]
        )
    ]
)