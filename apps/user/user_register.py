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

# Callback for populating user type and sex assigned at birth dropdown menus
@app.callback(
    [
        Output('user_type', 'options'),
        Output('user_assignedsex', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateusertypes(pathname):
    if pathname == '/user/register':
        sql1 = """
        SELECT usertype_name as label, usertype_id as value
        FROM userblock.usertype;
        """
        values1 = []
        cols1 = ['label', 'value']
        df1 = db.querydatafromdatabase(sql1, values1, cols1)
        
        user_types = df1.to_dict('records')

        sql2 = """
        SELECT assignedsex_name as label, assignedsex_code as value
        FROM userblock.assignedsex;
        """
        values2 = []
        cols2 = ['label', 'value']
        df2 = db.querydatafromdatabase(sql2, values2, cols2)
        
        user_assignedsex = df2.to_dict('records')
        return [user_types, user_assignedsex]
    else:
        raise PreventUpdate

# Callback for populating access type dropdown menu
@app.callback(
    [
        Output('accesstype_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateaccesstypes(pathname):
    if pathname == '/user/register':
        sql = """SELECT accesstype_name as label, accesstype_id as value
        FROM userblock.accesstype
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        accesstypes = df.to_dict('records')
        return [accesstypes]
    else: raise PreventUpdate

# Callback for populating college dropdown menu
@app.callback(
    [
        Output('college_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populatecolleges(pathname):
    if pathname == '/user/register':
        sql = """SELECT college_name as label, college_id as value
        FROM userblock.college
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        colleges = df.to_dict('records')
        return [colleges]
    else: raise PreventUpdate

# Callback for populating degree program dropdown menu
@app.callback(
    [
        Output('degree_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('college_id', 'value')
    ]
)

def register_populatedegrees(pathname, college_id):
    if pathname == '/user/register':
        if college_id:
            sql = """SELECT degree_name as label, degree_id as value
            FROM userblock.degreeprogram WHERE college_id = 
            """ + str(college_id)
            values = []
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols)
            
            degrees = df.to_dict('records')
            return [degrees]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for populating office dropdown menu
@app.callback(
    [
        Output('office_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateoffices(pathname):
    if pathname == '/user/register':
        sql = """SELECT office_name as label, office_id as value
        FROM userblock.office
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        offices = df.to_dict('records')
        return [offices]
    else: raise PreventUpdate

# Callback for showing user type-specific sections of the registration page
@app.callback(
        [
            Output('userspecific_form', 'children'),
            Output('user_id_label', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('user_type', 'value'),
        ]
)

def register_showspecificforms(pathname, user_type):
    if pathname == '/user/register':
        form_student = [
            #html.Hr(),
            #html.H3("Student Information"),
            dbc.Row(
                [
                    dbc.Label("College", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'college_id'
                        ), width = 9
                    )
                ], className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Degree Program", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'degree_id'
                        ), width = 9
                    ),
                ], className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Year level", width = 2),
                    dbc.Col(
                        dbc.Input(
                            type = 'text',
                            id = 'student_year',
                            placeholder = 'Year level'
                        ),
                        width = 3
                    )
                ], className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Access type", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'accesstype_id',
                            value = 1,
                            disabled = True
                        ), width = 3
                    ),
                    dbc.Label("Student ID No.", width = 3),
                    dbc.Col(
                        dbc.Input(
                            type = 'text',
                            id = 'student_id',
                            placeholder = 'Enter ID number',
                            disabled = True
                        ),
                        width = 3
                    )
                ],
                id = 'studentid_block',
                style = {'display' : 'none'}
            )
        ]
        form_faculty = [
            #html.Hr(),
            #html.H3("Faculty Information"),
            dbc.Row(
                [
                    dbc.Label("College", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'college_id'
                        ), width = 3
                    ),
                    dbc.Label("Designation", width = 3),
                    dbc.Col(
                        dbc.Input(
                            type = 'text',
                            id = 'faculty_desig',
                            placeholder = 'e.g. Instructor I, Professor II'
                        ),
                        width = 3
                    )
                ], className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Access type", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'accesstype_id',
                            value = 1
                        ), width = 3
                    ),
                    html.Div(
                        [
                            dbc.Label("Faculty ID No.", width = 3),
                            dbc.Col(
                                dbc.Input(
                                    type = 'text',
                                    id = 'faculty_id',
                                    placeholder = 'Enter ID number',
                                    disabled = True
                                ),
                                width = 3
                            )
                        ],
                        id = 'facultyid_block',
                        style = {'display' : 'none'}
                    )
                ]
            )
        ]
        form_staff = [
            #html.Hr(),
            #html.H3("Staff Information"),
            dbc.Row(
                [
                    dbc.Label("Office", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'office_id'
                        ), width = 3
                    ),
                    dbc.Label("Designation", width = 3),
                    dbc.Col(
                        dbc.Input(
                            type = 'text',
                            id = 'staff_desig',
                            placeholder = 'e.g. Registrar I, Librarian I'
                        ),
                        width = 3
                    )
                ], className = 'mb-3'
            ),
            dbc.Row(
                [
                    dbc.Label("Access type", width = 2),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'accesstype_id',
                            value = 1,
                        ), width = 3
                    ),
                    html.Div(
                        [
                            dbc.Label("Staff ID No.", width = 3),
                            dbc.Col(
                                dbc.Input(
                                    type = 'text',
                                    id = 'staff_id',
                                    placeholder = 'Enter ID number',
                                    disabled = True
                                ),
                                width = 3
                            )
                        ],
                        id = 'staffid_block',
                        style = {'display' : 'none'}
                    )
                ],
            )
        ]
        if user_type == None:
            return [None], 'ID No.'
        elif user_type == 1:
            return form_student, 'Student No.'
        elif user_type == 2:
            return form_faculty, 'Employee No.'
        elif user_type == 3:
            return form_staff, 'Employee No.'
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for setting student_id equal to user_id
@app.callback(
    [
        Output('student_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('user_id', 'value')
    ]
)

def set_studentid(pathname, user_id):
    if pathname == '/user/register':
        if user_id: return [user_id]
        else: return [None]
    raise PreventUpdate

# Callback for setting faculty_id equal to user_id
@app.callback(
    [
        Output('faculty_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('user_id', 'value')
    ]
)

def set_facultyid(pathname, user_id):
    if pathname == '/user/register':
        if user_id: return [user_id]
        else: return [None]
    raise PreventUpdate

# Callback for setting staff_id equal to user_id
@app.callback(
    [
        Output('staff_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('user_id', 'value')
    ]
)

def set_staffid(pathname, user_id):
    if pathname == '/user/register':
        if user_id: return [user_id]
        else: return [None]
    raise PreventUpdate

# Callback for populating regions
@app.callback(
    [
        Output('present_region_id', 'options'),
        Output('permanent_region_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateregions(pathname):
    if pathname == '/user/register':
        sql = """SELECT region_name as label, region_id as value
        FROM userblock.addressregion;
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        df = df.sort_values('value')

        regions = df.to_dict('records')
        return [regions, regions]
    else:
        raise PreventUpdate

# Callback for showing present province dropdown once present region is selected
@app.callback(
        [
            Output('present_province', 'children'),
            Output('present_province', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value')
        ]
)

def show_presentprovinces(pathname, present_region_id):
    dropdown_present_province = [
        dbc.Label("Province", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'present_province_id',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if present_region_id:
            return [dropdown_present_province, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for showing permanent province dropdown once permanent region is selected
@app.callback(
        [
            Output('permanent_province', 'children'),
            Output('permanent_province', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('permanent_region_id', 'value')
        ]
)

def show_permanentprovinces(pathname, permanent_region_id):
    dropdown_permanent_province = [
        dbc.Label("Province", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'permanent_province_id'
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if permanent_region_id:
            return [dropdown_permanent_province, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for populating present province dropdown
@app.callback(
    [
        Output('present_province_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('present_region_id', 'value')
    ]
)

def populate_presentprovinces(pathname, present_region_id):
    if pathname == '/user/register':
        if present_region_id:
            sql = """SELECT province_name as label, province_id as value
            FROM userblock.addressprovince WHERE region_id = 
            """
            values = []
            cols = ['label', 'value']
            sql += str(present_region_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for populating permanent province dropdown
@app.callback(
    [
        Output('permanent_province_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('permanent_region_id', 'value')
    ]
)

def populate_permanentprovinces(pathname, permanent_region_id):
    if pathname == '/user/register':
        if permanent_region_id:
            sql = """SELECT province_name as label, province_id as value
            FROM userblock.addressprovince WHERE region_id = 
            """
            values = []
            cols = ['label', 'value']
            sql += str(permanent_region_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present citymun dropdown once present province and region is selected
@app.callback(
        [
            Output('present_citymun', 'children'),
            Output('present_citymun', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value'),
            Input('present_province_id', 'value')
        ]
)

def show_presentcitymun(pathname, present_region_id, present_province_id):
    dropdown_present_citymun = [
        dbc.Label("City/Municipality", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'present_citymun_id',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if present_region_id and present_province_id:
            return [dropdown_present_citymun, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for showing permanent citymun dropdown once permanent province and region is selected
@app.callback(
        [
            Output('permanent_citymun', 'children'),
            Output('permanent_citymun', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('permanent_region_id', 'value'),
            Input('permanent_province_id', 'value')
        ]
)

def show_permanentcitymun(pathname, permanent_region_id, permanent_province_id):
    dropdown_permanent_citymun = [
        dbc.Label("City/Municipality", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'permanent_citymun_id',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if permanent_region_id and permanent_province_id:
            return [dropdown_permanent_citymun, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for populating present citymun dropdown
@app.callback(
    [
        Output('present_citymun_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('present_region_id', 'value'),
        Input('present_province_id', 'value')
    ]
)

def populate_presentcitymun(pathname, present_region_id, present_province_id):
    if pathname == '/user/register':
        if present_region_id and present_province_id:
            sql = """SELECT citymun_name as label, citymun_id as value
            FROM userblock.addresscitymun WHERE
            """
            values = []
            cols = ['label', 'value']
            sql += " region_id = "+str(present_region_id)+" AND province_id = "+str(present_province_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for populating permanent citymun dropdown
@app.callback(
    [
        Output('permanent_citymun_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('permanent_region_id', 'value'),
        Input('permanent_province_id', 'value')
    ]
)

def populate_permanentcitymun(pathname, permanent_region_id, permanent_province_id):
    if pathname == '/user/register':
        if permanent_region_id and permanent_province_id:
            sql = """SELECT citymun_name as label, citymun_id as value
            FROM userblock.addresscitymun WHERE
            """
            values = []
            cols = ['label', 'value']
            sql += " region_id = "+str(permanent_region_id)+" AND province_id = "+str(permanent_province_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present barangay dropdown once present province, region, and citymun is selected
@app.callback(
        [
            Output('present_barangay', 'children'),
            Output('present_barangay', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value'),
            Input('present_province_id', 'value'),
            Input('present_citymun_id', 'value')
        ]
)

def show_presentbrgy(pathname, present_region_id, present_province_id, present_citymun_id):
    dropdown_present_barangay = [
        dbc.Label("Barangay", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'present_brgy_id',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if present_region_id and present_province_id and present_citymun_id:
            return [dropdown_present_barangay, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for showing permanent barangay dropdown once permanent province, region, and citymun is selected
@app.callback(
        [
            Output('permanent_barangay', 'children'),
            Output('permanent_barangay', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('permanent_region_id', 'value'),
            Input('permanent_province_id', 'value'),
            Input('permanent_citymun_id', 'value')
        ]
)

def show_permanentbrgy(pathname, permanent_region_id, permanent_province_id, permanent_citymun_id):
    dropdown_permanent_barangay = [
        dbc.Label("Barangay", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'permanent_brgy_id',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if permanent_region_id and permanent_province_id and permanent_citymun_id:
            return [dropdown_permanent_barangay, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for populating present barangay dropdown
@app.callback(
    [
        Output('present_brgy_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('present_region_id', 'value'),
        Input('present_province_id', 'value'),
        Input('present_citymun_id', 'value')
    ]
)

def populate_presentbrgy(pathname, present_region_id, present_province_id, present_citymun_id):
    if pathname == '/user/register':
        if present_region_id and present_province_id and present_citymun_id:
            sql = """SELECT brgy_name as label, brgy_id as value
            FROM userblock.addressbarangay WHERE
            """
            values = []
            cols = ['label', 'value']
            sql += " region_id = "+str(present_region_id)+" AND province_id = "+str(present_province_id)+" AND citymun_id = "+str(present_citymun_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for populating permanent barangay dropdown
@app.callback(
    [
        Output('permanent_brgy_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('permanent_region_id', 'value'),
        Input('permanent_province_id', 'value'),
        Input('permanent_citymun_id', 'value')
    ]
)

def populate_permanentbrgy(pathname, permanent_region_id, permanent_province_id, permanent_citymun_id):
    if pathname == '/user/register':
        if permanent_region_id and permanent_province_id and permanent_citymun_id:
            sql = """SELECT brgy_name as label, brgy_id as value
            FROM userblock.addressbarangay WHERE
            """
            values = []
            cols = ['label', 'value']
            sql += " region_id = "+str(permanent_region_id)+" AND province_id = "+str(permanent_province_id)+" AND citymun_id = "+str(permanent_citymun_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present street address input once permanent province, region, citymun, and barangay is selected
@app.callback(
        [
            Output('present_street_input', 'children'),
            Output('present_street_input', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value'),
            Input('present_province_id', 'value'),
            Input('present_citymun_id', 'value'),
            Input('present_brgy_id', 'value')
        ]
)

def show_presentstreet(pathname, present_region_id, present_province_id, present_citymun_id, present_brgy_id):
    input_present_street = [
        dbc.Label("Street address", width = 2),
        dbc.Col(
            dbc.Input(
                id = 'present_street',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if present_region_id and present_province_id and present_citymun_id and present_brgy_id:
            return [input_present_street, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for showing permanent street address input once permanent province, region, citymun, and barangay is selected
@app.callback(
        [
            Output('permanent_street_input', 'children'),
            Output('permanent_street_input', 'className')
        ],
        [
            Input('url', 'pathname'),
            Input('permanent_region_id', 'value'),
            Input('permanent_province_id', 'value'),
            Input('permanent_citymun_id', 'value'),
            Input('permanent_brgy_id', 'value')
        ]
)

def show_permanentstreet(pathname, permanent_region_id, permanent_prov_id, permanent_citymun_id, permanent_brgy_id):
    input_permanent_street = [
        dbc.Label("Street address", width = 2),
        dbc.Col(
            dbc.Input(
                id = 'permanent_street',
            ), width = 9
        )
    ]
    if pathname == '/user/register':
        if permanent_region_id and permanent_prov_id and permanent_citymun_id and permanent_brgy_id:
            return [input_permanent_street, 'mb-3']
        else: return [None, None]
    else: raise PreventUpdate

# Callback for automatically generating username and checking existing list of usernames
@app.callback(
    [
        Output('user_username', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('user_fname', 'value'),
        Input('user_mname', 'value'),
        Input('user_lname', 'value'),
    ]
)

def generate_username(pathname, user_fname, user_mname, user_lname):
    if pathname == '/user/register':
        if user_fname and user_mname and user_lname:
            user_username = user_fname[0]+user_mname[0]+user_lname
        elif user_fname and user_lname:
            user_username = user_fname[0]+user_lname
        else: user_username = None

        if user_username:
            sql = """SELECT user_username
                FROM userblock.RegisteredUser
                WHERE user_username LIKE %s;"""
            values = [f"%{user_username.lower()}%"]
            cols = ['user_username']
            df = db.querydatafromdatabase(sql, values, cols)
            #print(df)
            df = df[df['user_username'] == user_username.lower()]
            #print(df)
            
            if not df.empty:
                lastchar = df.tail().values[0][0][-1]
                if lastchar.isnumeric():
                    return [user_username.lower()+str(int(lastchar)+1)]
                else:
                    return [user_username.lower()+"1"]
            else:
                return [user_username.lower()]

        return [None]
    else: raise PreventUpdate

"""@app.callback(
    [
        Output('register_confirmationmodal', 'is_open'),
        Output('register_confirmationmodal', 'children')
    ],
    [
        Input('register_btn', 'n_clicks')
    ],
    [
        # Basic information
        State('user_id', 'value'),
        State('user_type', 'value'),
        State('user_lname', 'value'),
        State('user_fname', 'value'),
        State('user_mname', 'value'),
        State('user_username', 'value'),
        State('user_birthdate', 'value'),
        State('user_assignedsex', 'value'),
        # Contact details
        State('user_email', 'value'),
        State('user_contactnum', 'value'),
        # Present address
        State('present_region_id', 'value'),
        State('present_province_id', 'value'),
        State('present_citymun_id', 'value'),
        State('present_brgy_id', 'value'),
        State('present_street', 'value'),
        # Permanent address
        State('permanent_region_id', 'value'),
        State('permanent_province_id', 'value'),
        State('permanent_citymun_id', 'value'),
        State('permanent_brgy_id', 'value'),
        State('permanent_street', 'value'),
        # Optional information
        State('user_pronouns', 'value'),
        State('user_honorific', 'value'),
        State('user_livedname', 'value'),
        # Student information
        State('student_id', 'value'),
        State('student_year', 'value'),
        State('degree_id', 'value'),
        # Student and faculty information
        State('college_id', 'value'),
        # Faculty information
        State('faculty_id', 'value'),
        State('faculty_desig', 'value'),
        # Staff information
        State('staff_id', 'value'),
        State('staff_desig', 'value'),
        State('office_id', 'value'),
    ]
)

def confirmation(btn, user_id, user_type, lname, fname, mname,
                 username, birthdate, assignedsex, email, contactnum,
                 present_region, present_province, present_citymun, present_brgy, present_street,
                 permanent_region, permanent_province, permanent_citymun, permanent_brgy, permanent_street,
                 pronouns, honorific, livedname, student_id, student_year, degree, college,
                 faculty_id, faculty_desig, staff_id, staff_desig, office):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'register_btn' and btn:"""
            

layout = html.Div(
    [
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.H1(['Register User']),
                        html.Hr(),
                        dbc.Form(
                            [
                                html.Div(
                                    [
                                        dbc.Row(
                                            [
                                                dbc.Label ("User type", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(id = 'user_type'), width = 3
                                                ),
                                                dbc.Label("ID No.", id = 'user_id_label', width = 3),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_id',
                                                        placeholder = 'Enter ID number'
                                                    ), width = 3
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        html.Div(id = 'userspecific_form'),
                                        html.Hr(),
                                        html.H3("Basic Information"),
                                        dbc.Row(
                                            [
                                                dbc.Label("Name", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_lname',
                                                        placeholder = 'Enter surname'
                                                    ), width = 3
                                                ),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_fname',
                                                        placeholder = 'Enter first name'
                                                    ), width = 3
                                                ),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_mname',
                                                        placeholder = 'Enter middle name'
                                                    ), width = 3
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Username", width = 2, id = 'user_username_label'),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_username',
                                                        placeholder = 'Username',
                                                        disabled = True,
                                                    ), width = 9
                                                ),
                                                dbc.Tooltip(
                                                    """Usernames are generated automatically.""",
                                                    target = 'user_username_label'
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Date of birth", width = 2),
                                                dbc.Col(
                                                    dcc.DatePickerSingle(
                                                        id = 'user_birthdate',
                                                        placeholder = 'MM/DD/YYYY',
                                                        month_format = 'MMM Do, YYYY'
                                                    ), width = 3
                                                ),
                                                dbc.Label ("Sex assigned at birth", width = 3),
                                                dbc.Col(
                                                    dcc.Dropdown(id = 'user_assignedsex'), width = 3
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label ("Contact number", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_contactnum',
                                                        placeholder = '09XXXXXXXXX'
                                                    ), width = 3
                                                ),
                                                dbc.Label ("Email address", width = 3, id = 'user_email_label'),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_email',
                                                        placeholder = 'example@nwssu.edu.ph'
                                                    ), width = 3
                                                ),
                                                dbc.Tooltip(
                                                    """You are encouraged to input your NwSSU email address.""",
                                                    target = 'user_email_label'
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        html.Hr(),
                                    ], id = 'basic_information'
                                ),
                                html.Div(
                                    [
                                        html.H3("Present Address"),
                                        dbc.Row(
                                            [
                                                dbc.Label("Region", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'present_region_id'
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(id = 'present_province'),
                                        dbc.Row(id = 'present_citymun'),
                                        dbc.Row(id = 'present_barangay'),
                                        dbc.Row(id = 'present_street_input'),
                                        html.Hr(),
                                    ], 
                                    id = 'present_address'
                                ),
                                html.Div(
                                    [
                                        html.H3("Permanent Address"),
                                        dbc.Row(
                                            [
                                                dbc.Label("Region", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'permanent_region_id'
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(id = 'permanent_province'),
                                        dbc.Row(id = 'permanent_citymun'),
                                        dbc.Row(id = 'permanent_barangay'),
                                        dbc.Row(id = 'permanent_street_input'),
                                        html.Hr(),
                                    ], 
                                    id = 'permanent_address'
                                ),
                                html.Div(
                                    [
                                        html.H3("Optional information"),
                                        dbc.Row(
                                            [
                                                dbc.Label("Pronouns", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_pronouns',
                                                        placeholder = 'E.g. they/them, she/her, he/him'
                                                    ), width = 3
                                                ),
                                                dbc.Label("Preferred honorific", width = 3),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_honorific',
                                                        placeholder = 'E.g. Mx., Mrs., Ms., Mr., Dr.'
                                                    ), width = 3
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Lived name", width = 2, id = 'user_livedname_label'),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_livedname',
                                                        placeholder = 'Enter lived name'
                                                    ), width = 9
                                                ),
                                                dbc.Tooltip(
                                                    """Per Memorandum No. OVCAA-MTTP 21-029 of the Vice Chancellor for Academic Affairs of UP Diliman, a
                                                    lived name is a name that affirms one's gender identity and/or expression (GIE).""",
                                                    target = 'user_livedname_label'
                                                )
                                            ], className = 'mb-3'
                                        ),
                                    ], id = 'optional_information'
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Register", color = 'primary', id = 'register_btn'
                            )
                        )
                    ]
                )
            ]
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(
                    html.H4('Confirm details')
                ),
                dbc.ModalBody(
                    'Edit me'
                ),
                dbc.ModalFooter(
                    dbc.Button(
                        "Confirm", href = '/user/profile'
                    )
                )
            ],
            centered = True,
            id = 'register_confirmationmodal',
            backdrop = 'static'
        )
    ]
)