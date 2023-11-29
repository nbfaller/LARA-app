from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
#import dash_ag_grid as dag

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

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
        FROM utilities.usertype;
        """
        values1 = []
        cols1 = ['label', 'value']
        df1 = db.querydatafromdatabase(sql1, values1, cols1)
        
        user_types = df1.to_dict('records')

        sql2 = """
        SELECT assignedsex_name as label, assignedsex_code as value
        FROM utilities.assignedsex;
        """
        values2 = []
        cols2 = ['label', 'value']
        df2 = db.querydatafromdatabase(sql2, values2, cols2)
        
        user_assignedsex = df2.to_dict('records')
        return [user_types, user_assignedsex]
    else:
        raise PreventUpdate

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

@app.callback(
    [
        Output('office_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

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
                        ), width = 3
                    ),
                    dbc.Label("Degree Program", width = 3),
                    dbc.Col(
                        dcc.Dropdown(
                            id = 'degree_id'
                        ), width = 3
                    ),
                ]
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
                ]
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
                ]
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

@app.callback(
    [Output('address_region', 'options')],
    [Input('url', 'pathname')]
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
        return [regions]
    else:
        raise PreventUpdate

@app.callback(
        [
            Output('present_province', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('address_region', 'value')
        ]
)

def show_addressprovince(pathname, region_id):
    dropdown_province = [
        dbc.Label("Province", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'address_province',
            ), width = 6
        )
    ]
    if pathname == '/user/register':
        if region_id:
            return [dropdown_province]
        elif region_id == None: return [None]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
        [
            Output('present_citymun', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('address_region', 'value'),
            Input('address_province', 'value')
        ]
)

def show_addresscitymun(pathname, region_id, prov_id):
    dropdown_citymun = [
        dbc.Label("City/Municipality", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'address_citymun',
            ), width = 6
        )
    ]
    if pathname == '/user/register':
        if region_id and prov_id:
            return [dropdown_citymun]
        elif region_id == None or prov_id == None: return [None]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
        [
            Output('present_barangay', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('address_region', 'value'),
            Input('address_province', 'value'),
            Input('address_citymun', 'value')
        ]
)

def show_addressbarangay(pathname, region_id, prov_id, citymun_id):
    dropdown_barangay = [
        dbc.Label("Barangay", width = 2),
        dbc.Col(
            dcc.Dropdown(
                id = 'address_barangay',
            ), width = 6
        )
    ]
    if pathname == '/user/register':
        if region_id and prov_id and citymun_id:
            return [dropdown_barangay]
        elif region_id == None or prov_id == None or citymun_id == None: return [None]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
        [
            Output('present_street', 'children')
        ],
        [
            Input('url', 'pathname'),
            Input('address_region', 'value'),
            Input('address_province', 'value'),
            Input('address_citymun', 'value'),
            Input('address_barangay', 'value')
        ]
)

def show_addressstreet(pathname, region_id, prov_id, citymun_id, brgy_id):
    input_street = [
        dbc.Label("Street address", width = 2),
        dbc.Col(
            dbc.Input(
                id = 'address_street',
            ), width = 6
        )
    ]
    if pathname == '/user/register':
        if region_id and prov_id and citymun_id and brgy_id:
            return [input_street]
        elif region_id == None or prov_id == None or citymun_id == None or brgy_id == None: return [None]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
    [
        Output('address_province', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('address_region', 'value')
    ]
)

def register_populateprovinces(pathname, region_id):
    if pathname == '/user/register':
        if region_id:
            sql = """SELECT province_name as label, province_id as value
            FROM userblock.addressprovince WHERE region_id = 
            """
            values = []
            cols = ['label', 'value']

            if region_id:
                sql += str(region_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            #print(sql)
            provinces = df.to_dict('records')
            return [provinces]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
    [
        Output('address_citymun', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('address_province', 'value'),
        Input('address_region', 'value')
    ]
)

def register_populatecitymun(pathname, province_id, region_id):
    if pathname == '/user/register':
        if region_id and province_id:
            sql = """SELECT citymun_name as label, citymun_id as value
            FROM userblock.addresscitymun WHERE 
            """
            values = []
            cols = ['label', 'value']

            if province_id:
                sql += ' province_id = '+str(province_id)+' AND region_id = '+str(region_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            citymun = df.to_dict('records')
            return [citymun]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
    [
        Output('address_barangay', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('address_citymun', 'value'),
        Input('address_region', 'value'),
        Input('address_province', 'value')
    ]
)

def register_populatebarangay(pathname, citymun_id, region_id, province_id):
    if pathname == '/user/register':
        if region_id and province_id and citymun_id:
            sql = """SELECT brgy_name as label, brgy_id as value
            FROM userblock.addressbarangay WHERE 
            """
            values = []
            cols = ['label', 'value']

            if citymun_id:
                sql += 'citymun_id = '+str(citymun_id)+' AND province_id = '+str(province_id)+' AND region_id = '+str(region_id)+";"

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            barangay = df.to_dict('records')
            return [barangay]
        else: raise PreventUpdate
    else: raise PreventUpdate

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
                                                dbc.Label("Surname", width = 2),
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
                                                dbc.Label ("Email address", width = 3),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_emailaddress',
                                                        placeholder = 'example@nwssu.edu.ph'
                                                    ), width = 3
                                                )
                                            ]
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
                                                        id = 'address_region'
                                                    ), width = 6
                                                )
                                            ]
                                        ),
                                        dbc.Row(id = 'present_province'),
                                        dbc.Row(id = 'present_citymun'),
                                        dbc.Row(id = 'present_barangay'),
                                        dbc.Row(id = 'present_street'),
                                        html.Hr(),
                                    ], 
                                    id = 'present_address'
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
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Preferred honorific", width = 2),
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
                                                dbc.Label("Lived name", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        type = 'text',
                                                        id = 'user_livedname',
                                                        placeholder = 'Enter lived name'
                                                    ), width = 3
                                                )
                                            ], className = 'mb-3'
                                        ),
                                    ], id = 'optional_information'
                                )
                            ]
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Register", color = 'primary', id = 'login_loginbtn'
                            )
                        )
                    ]
                )
            ]
        )
    ]
)