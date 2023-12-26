from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import numpy
from urllib.parse import urlparse, parse_qs

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

import hashlib

# Callback for retrieving page mode and profile id
@app.callback(
    [
        Output('page_mode', 'data'),
        Output('view_id', 'data')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)

def set_pagemode(pathname, search):
    mode = 'view'
    user_id = None
    if pathname == '/user/profile':
        parsed = urlparse(search)
        if parse_qs(parsed.query):
            mode = parse_qs(parsed.query)['mode'][0]
            if parsed.query.find("&") > -1:
                user_id = parse_qs(parsed.query)['id'][0]
        return [mode, user_id]
    else: raise PreventUpdate

# Callback for populating values if mode is 'view'
@app.callback(
    [
        Output('profile_header', 'children'),
        # Primary information
        Output('usertype_id', 'value'), Output('usertype_id', 'disabled'),
        Output('user_id', 'value'), Output('user_id', 'disabled'),
        # Basic information
        Output('user_lname', 'value'), Output('user_lname', 'disabled'),
        Output('user_fname', 'value'), Output('user_fname', 'disabled'),
        Output('user_mname', 'value'), Output('user_mname', 'disabled'),
        #Output('user_username', 'value'),
        Output('user_birthdate', 'date'), Output('user_birthdate', 'disabled'),
        Output('user_assignedsex', 'value'), Output('user_assignedsex', 'disabled'),
        Output('user_contactnum', 'value'), Output('user_contactnum', 'disabled'),
        Output('user_email', 'value'), Output('user_email', 'disabled'),
        Output('present_region_id', 'value'), Output('present_region_id', 'disabled'),
        Output('permanent_region_id', 'value'), Output('permanent_region_id', 'disabled')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('page_mode', 'data'),
        State('view_id', 'data')
    ]
)

def view_populatevalues (pathname, mode, user_id):
    if pathname == '/user/profile':
        if mode == 'view':
            if user_id:
                sql = """SELECT u_t.usertype_name as type, u.usertype_id as usertype, u.user_lname as lname, u.user_fname as fname, u.user_mname as mname,
                u.user_username as username, u.user_birthdate as birthdate, u_as.assignedsex_id as assignedsex,
                u.user_contactnum as contactnum, u.user_email as email,
                pre_add.region_id as presentregion, pre_add.province_id as presentprovince, pre_add.citymun_id as presentcitymun, pre_add.brgy_id as presentbrgy, u.present_street as presentstreet,
                per_add.region_id as permanentregion, per_add.province_id as permanentprovince, per_add.citymun_id as permanentcitymun, per_add.brgy_id as permanentbrgy, u.permanent_street as permanentstreet
                FROM userblock.registereduser AS u
                INNER JOIN utilities.usertype AS u_t on u.usertype_id = u_t.usertype_id
                INNER JOIN utilities.assignedsex AS u_as on u.user_assignedsex = u_as.assignedsex_code
                INNER JOIN utilities.addressbarangay AS pre_add on u.present_brgy_id = pre_add.brgy_id AND u.present_citymun_id = pre_add.citymun_id AND u.present_province_id = pre_add.province_id AND u.present_region_id = pre_add.region_id
                INNER JOIN utilities.addressbarangay AS per_add on u.permanent_brgy_id = per_add.brgy_id AND u.permanent_citymun_id = per_add.citymun_id AND u.permanent_province_id = per_add.province_id AND u.permanent_region_id = per_add.region_id
                WHERE u.user_id = %s AND NOT u.userstatus_id = 4;"""
                values = [user_id]
                cols = [
                    'type',
                    'usertype', 'lname', 'fname', 'mname',
                    'username', 'birthdate', 'assignedsex',
                    'contactnum', 'email',
                    'presentregion', 'presentprovince', 'presentcitymun', 'presentbrgy', 'presentstreet',
                    'permanentregion', 'permanentprovince', 'permanentcitymun', 'permanentbrgy', 'permanentstreet'
                ]
                df = db.querydatafromdatabase(sql, values, cols)
                if df.shape:
                    #print(df)
                    header = [
                        html.P(
                            [
                                '%s • %s' % (df['type'][0], df['username'][0])
                            ], className = 'badge'
                        ),
                        html.H1("%s, %s %s" % (df['lname'][0], df['fname'][0], df['mname'][0]))
                    ]
                    return [
                        header,
                        df['usertype'][0], True, user_id, True,
                        df['lname'][0], True, df['fname'][0], True, df['mname'][0], True,
                        #df['username'][0],
                        df['birthdate'][0], True, df['assignedsex'][0], True,
                        df['contactnum'][0], True, df['email'][0], True,
                        df['presentregion'][0], True, #df['presentprovince'][0], True, df['presentcitymun'][0], True, df['presentbrgy'][0], True, df['presentstreet'][0], True,
                        df['permanentregion'][0], True, #df['permanentprovince'][0], True, df['permanentcitymun'][0], True, df['permanentbrgy'][0], True, df['permanentstreet'][0], True
                    ]
                else: raise PreventUpdate
            else: raise PreventUpdate
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for populating user type and sex assigned at birth dropdown menus
@app.callback(
    [
        Output('usertype_id', 'options'),
        Output('user_assignedsex', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateusertypes(pathname):
    if pathname == '/user/profile':
        sql1 = """
        SELECT usertype_name as label, usertype_id as value
        FROM utilities.usertype;
        """
        values1 = []
        cols1 = ['label', 'value']
        df1 = db.querydatafromdatabase(sql1, values1, cols1)
        
        user_types = df1.to_dict('records')

        sql2 = """
        SELECT assignedsex_name as label, assignedsex_id as value
        FROM utilities.assignedsex;
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
        Output('student_accesstype_id', 'options'),
        Output('faculty_accesstype_id', 'options'),
        Output('staff_accesstype_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateaccesstypes(pathname):
    if pathname == '/user/profile':
        sql = """SELECT accesstype_name as label, accesstype_id as value
        FROM utilities.accesstype
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        accesstypes = df.to_dict('records')
        return [accesstypes, accesstypes, accesstypes]
    else: raise PreventUpdate

# Callback for populating college dropdown menu
@app.callback(
    [
        Output('student_college_id', 'options'),
        Output('faculty_college_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populatecolleges(pathname):
    if pathname == '/user/profile':
        sql = """SELECT college_name as label, college_id as value
        FROM utilities.college
        """
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
        
        colleges = df.to_dict('records')
        return [colleges, colleges]
    else: raise PreventUpdate

# Callback for populating degree program dropdown menu
@app.callback(
    [
        Output('degree_id', 'disabled'),
        Output('degree_id', 'options'),
        Output('degree_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('student_college_id', 'value')
    ]
)

def register_populatedegrees(pathname, student_college_id):
    if pathname == '/user/profile':
        degrees = []
        if student_college_id:
            sql = """SELECT degree_name as label, degree_id as value
            FROM utilities.degreeprogram WHERE college_id = %s;
            """
            values = [student_college_id]
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols)
            degrees = df.to_dict('records')
            return [False, degrees, None]
        else: return [True, degrees, None]
    else: raise PreventUpdate

# Callback for populating year level dropdown menu
@app.callback(
    [
        Output('year_id', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def register_populateyearlevels(pathname):
    if pathname == '/user/profile':
        sql = """SELECT year_level as label, year_id as value
        FROM utilities.yearlevel"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols)
            
        year_levels = df.to_dict('records')
        return [year_levels]
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
    if pathname == '/user/profile':
        sql = """SELECT office_name as label, office_id as value
        FROM utilities.office
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
            Output('student_form', 'style'), Output('faculty_form', 'style'), Output('staff_form', 'style'), Output('user_id_label', 'children'),
            Output('student_college_id', 'value'), Output('year_id', 'value'),
            Output('faculty_college_id', 'value'), Output('faculty_desig', 'value'), Output('faculty_accesstype_id', 'value'),
            Output('office_id', 'value'), Output('staff_desig', 'value'), Output('staff_accesstype_id', 'value')
        ],
        [
            Input('url', 'pathname'),
            Input('usertype_id', 'value'),
        ]
)

def register_showspecificforms(pathname, usertype_id):
    if pathname == '/user/profile':
        blank = {'display': 'none'}
        show = {'display': 'block'}
        if usertype_id == None:
            return [
                blank, blank, blank, 'ID No.',
                None, None,
                None, None, 1,
                None, None, 1
            ]
        elif usertype_id == 1:
            return [
                show, blank, blank, 'Student No.',
                None, None,
                None, None, 1,
                None, None, 1
            ]
        elif usertype_id == 2:
            return [
                blank, show, blank, 'Employee No.',
                None, None,
                None, None, 1,
                None, None, 1
            ]
        elif usertype_id == 3:
            return [
                blank, blank, show, 'Employee No.',
                None, None,
                None, None, 1,
                None, None, 1
            ]
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
    if pathname == '/user/profile':
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
    if pathname == '/user/profile':
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
    if pathname == '/user/profile':
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
    if pathname == '/user/profile':
        sql = """SELECT region_name as label, region_id as value
        FROM utilities.addressregion;
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
        Output('present_province_id', 'disabled'),
        Output('present_province_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('present_region_id', 'value')
    ],
    [
        State('page_mode', 'data'),
        State('view_id', 'data')
    ]
)

def show_presentprovinces(pathname, present_region_id, mode, user_id):
    disabled = True
    value = None
    if pathname == '/user/profile':
        if present_region_id:
            if mode == 'view' and user_id:
                sql = """SELECT u.present_province_id as province
                FROM userblock.registereduser AS u
                WHERE u.user_id = %s AND NOT u.userstatus_id = 4;
                """
                values = [user_id]
                cols = ['province']
                df = db.querydatafromdatabase(sql, values, cols)
                value = df['province'][0]
            else: disabled = False
        return [disabled, value]
    else: raise PreventUpdate

# Callback for showing permanent province dropdown once permanent region is selected
@app.callback(
    [
        Output('permanent_province_id', 'disabled'),
        Output('permanent_province_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('permanent_region_id', 'value')
    ],
    [
        State('page_mode', 'data'),
        State('view_id', 'data')
    ]
)

def show_permanentprovinces(pathname, permanent_region_id, mode, user_id):
    disabled = True
    value = None
    if pathname == '/user/profile':
        if permanent_region_id:
            if mode == 'view' and user_id:
                sql = """SELECT u.permanent_province_id as province
                FROM userblock.registereduser AS u
                WHERE u.user_id = %s AND NOT u.userstatus_id = 4;
                """
                values = [user_id]
                cols = ['province']
                df = db.querydatafromdatabase(sql, values, cols)
                value = df['province'][0]
            else: disabled = False
        return [disabled, value]
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
    if pathname == '/user/profile':
        if present_region_id:
            sql = """SELECT province_name as label, province_id as value
            FROM utilities.addressprovince WHERE region_id = %s;
            """
            values = [present_region_id]
            cols = ['label', 'value']

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
    if pathname == '/user/profile':
        if permanent_region_id:
            sql = """SELECT province_name as label, province_id as value
            FROM utilities.addressprovince WHERE region_id = %s;
            """
            values = [permanent_region_id]
            cols = ['label', 'value']

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present citymun dropdown once present province and region is selected
@app.callback(
        [
            Output('present_citymun_id', 'disabled'),
            Output('present_citymun_id', 'value')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value'),
            Input('present_province_id', 'value')
        ]
)

def show_presentcitymun(pathname, present_region_id, present_province_id):
    if pathname == '/user/profile':
        if present_region_id and present_province_id:
            return [False, None]
        else: return [True, None]
    else: raise PreventUpdate

# Callback for showing permanent citymun dropdown once permanent province and region is selected
@app.callback(
    [
        Output('permanent_citymun_id', 'disabled'),
        Output('permanent_citymun_id', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('permanent_region_id', 'value'),
        Input('permanent_province_id', 'value')
    ]
)

def show_permanentcitymun(pathname, permanent_region_id, permanent_province_id):
    if pathname == '/user/profile':
        if permanent_region_id and permanent_province_id:
            return [False, None]
        else: return [True, None]
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
    if pathname == '/user/profile':
        if present_region_id and present_province_id:
            sql = """SELECT citymun_name as label, citymun_id as value
            FROM utilities.addresscitymun WHERE region_id = %s AND province_id = %s;
            """
            values = [present_region_id, present_province_id]
            cols = ['label', 'value']

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
    if pathname == '/user/profile':
        if permanent_region_id and permanent_province_id:
            sql = """SELECT citymun_name as label, citymun_id as value
            FROM utilities.addresscitymun WHERE region_id = %s AND province_id = %s;
            """
            values = [permanent_region_id, permanent_province_id]
            cols = ['label', 'value']

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present barangay dropdown once present province, region, and citymun is selected
@app.callback(
        [
            Output('present_brgy_id', 'disabled'),
            Output('present_brgy_id', 'value')
        ],
        [
            Input('url', 'pathname'),
            Input('present_region_id', 'value'),
            Input('present_province_id', 'value'),
            Input('present_citymun_id', 'value')
        ]
)

def show_presentbrgy(pathname, present_region_id, present_province_id, present_citymun_id):
    if pathname == '/user/profile':
        if present_region_id and present_province_id and present_citymun_id:
            return [False, None]
        else: return [True, None]
    else: raise PreventUpdate

# Callback for showing permanent barangay dropdown once permanent province, region, and citymun is selected
@app.callback(
        [
            Output('permanent_brgy_id', 'disabled'),
            Output('permanent_brgy_id', 'value')
        ],
        [
            Input('url', 'pathname'),
            Input('permanent_region_id', 'value'),
            Input('permanent_province_id', 'value'),
            Input('permanent_citymun_id', 'value')
        ]
)

def show_permanentbrgy(pathname, permanent_region_id, permanent_province_id, permanent_citymun_id):
    if pathname == '/user/profile':
        if permanent_region_id and permanent_province_id and permanent_citymun_id:
            return [False, None]
        else: return [True, None]
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
    if pathname == '/user/profile':
        if present_region_id and present_province_id and present_citymun_id:
            sql = """SELECT brgy_name as label, brgy_id as value
            FROM utilities.addressbarangay WHERE region_id = %s AND province_id = %s AND citymun_id = %s;
            """
            values = [present_region_id, present_province_id, present_citymun_id]
            cols = ['label', 'value']

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
    if pathname == '/user/profile':
        if permanent_region_id and permanent_province_id and permanent_citymun_id:
            sql = """SELECT brgy_name as label, brgy_id as value
            FROM utilities.addressbarangay WHERE region_id = %s AND province_id = %s AND citymun_id = %s;
            """
            values = [permanent_region_id, permanent_province_id, permanent_citymun_id]
            cols = ['label', 'value']

            df = db.querydatafromdatabase(sql, values, cols)
            df = df.sort_values('value')

            return [df.to_dict('records')]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for showing present street address input once permanent province, region, citymun, and barangay is selected
@app.callback(
        [
            Output('present_street', 'disabled'),
            Output('present_street', 'value')
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
    if pathname == '/user/profile':
        if present_region_id and present_province_id and present_citymun_id and present_brgy_id:
            return [False, None]
        else: return [True, None]
    else: raise PreventUpdate

# Callback for showing permanent street address input once permanent province, region, citymun, and barangay is selected
@app.callback(
        [
            Output('permanent_street', 'disabled'),
            Output('permanent_street', 'value')
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
    if pathname == '/user/profile':
        if permanent_region_id and permanent_prov_id and permanent_citymun_id and permanent_brgy_id:
            return [False, None]
        else: return [True, None]
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
    if pathname == '/user/profile':
        if user_fname and user_mname and user_lname:
            user_username = user_fname[0]+user_mname[0]+user_lname
        elif user_fname and user_lname:
            user_username = user_fname[0]+user_lname
        else: user_username = None

        if user_username:
            user_username = user_username.replace(" ", "")
            user_username = user_username.replace("-", "")
            #user_username = user_username.replace("ñ", "n")
            sql = """SELECT user_username
                FROM userblock.RegisteredUser
                WHERE user_username LIKE %s;"""
            values = [f"%{user_username.lower()}%"]
            cols = ['user_username']
            df = db.querydatafromdatabase(sql, values, cols)
            df = df[df['user_username'] == user_username.lower()]
            
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

@app.callback(
    [
        Output('register_alert', 'color'),
        Output('register_alert', 'children'),
        Output('register_alert', 'is_open'),

        Output('register_confirmationmodal', 'is_open'),
        Output('register_modalbody', 'children'),
    ],
    [
        Input('register_btn', 'n_clicks')
    ],
    [
        # Basic information
        State('user_id', 'value'),
        State('usertype_id', 'value'),
        State('user_lname', 'value'),
        State('user_fname', 'value'),
        State('user_mname', 'value'),
        State('user_username', 'value'),
        State('user_birthdate', 'date'),
        State('user_assignedsex', 'value'),

        # Contact information
        State('user_contactnum', 'value'),
        State('user_email', 'value'),

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
        State('student_college_id', 'value'),
        State('degree_id', 'value'),
        State('year_id', 'value'),

        # Faculty information
        State('faculty_college_id', 'value'),
        State('faculty_desig', 'value'),
        State('faculty_accesstype_id', 'value'),

        # Staff information
        State('office_id', 'value'),
        State('staff_desig', 'value'),
        State('staff_accesstype_id', 'value'),
    ]
)

def confirmation(btn, user_id, user_type, lname, fname, mname, username,
                 birthdate, assignedsex,
                 contactnum, email,
                 present_region, present_province, present_citymun, present_brgy, present_street,
                 permanent_region, permanent_province, permanent_citymun, permanent_brgy, permanent_street,
                 pronouns, honorific, livedname,
                 student_college, degree, year_level,
                 faculty_college, faculty_desig, faculty_accesstype,
                 office, staff_desig, staff_accesstype,
                 ):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'register_btn' and btn:
            alert_color = ''
            alert_text = ''
            alert_open = False
            modal_open = False
            modal_content = ''

            if (user_id == None or user_type == None or lname == None or fname == None or username == None
                or birthdate == None or assignedsex == None
                or contactnum == None or email == None
                or present_region == None or present_province == None or present_citymun == None or present_brgy == None or present_street == ''
                or permanent_region == None or permanent_province == None or permanent_citymun == None or permanent_brgy == None or permanent_street == ''):
                    alert_color = 'warning'
                    alert_open = True
                    alert_text = "Insufficient information."
                    return [alert_color, alert_text, alert_open, modal_open, modal_content]
            else:
                modal_open = True

                present_address = present_street+", "
                permanent_address = permanent_street+", "

                # Generating present address using sql query
                sql = """ SELECT add_b.brgy_name AS brgy, add_c.citymun_name AS citymun, add_p.province_name AS province, add_r.region_name AS region
                FROM utilities.addressbarangay AS add_b
                INNER JOIN utilities.addresscitymun AS add_c ON add_b.citymun_id = add_c.citymun_id AND add_b.province_id = add_c.province_id AND add_b.region_id = add_c.region_id
                INNER JOIN utilities.addressprovince AS add_p ON add_b.province_id = add_p.province_id AND add_b.region_id = add_p.region_id
                INNER JOIN utilities.addressregion AS add_r ON add_b.region_id = add_r.region_id
                WHERE add_b.region_id = %s AND add_b.province_id = %s AND add_b.citymun_id = %s AND add_b.brgy_id = %s;"""

                values = [present_region, present_province, present_citymun, present_brgy]
                cols = ['brgy', 'citymun', 'province', 'region']
                df = db.querydatafromdatabase(sql, values, cols)
                present_address += "Brgy. " + df['brgy'][0] + ", " + df['citymun'][0] + ", " + df['province'][0] + ", " + df['region'][0]

                # Generating permanent address using sql query
                sql = """ SELECT add_b.brgy_name AS brgy, add_c.citymun_name AS citymun, add_p.province_name AS province, add_r.region_name AS region
                FROM utilities.addressbarangay AS add_b
                INNER JOIN utilities.addresscitymun AS add_c ON add_b.citymun_id = add_c.citymun_id AND add_b.province_id = add_c.province_id AND add_b.region_id = add_c.region_id
                INNER JOIN utilities.addressprovince AS add_p ON add_b.province_id = add_p.province_id AND add_b.region_id = add_p.region_id
                INNER JOIN utilities.addressregion AS add_r ON add_b.region_id = add_r.region_id
                WHERE add_b.region_id = %s AND add_b.province_id = %s AND add_b.citymun_id = %s AND add_b.brgy_id = %s;"""

                values = [permanent_region, permanent_province, permanent_citymun, permanent_brgy]
                cols = ['brgy', 'citymun', 'province', 'region']
                df = db.querydatafromdatabase(sql, values, cols)
                permanent_address += "Brgy. " + df['brgy'][0] + ", " + df['citymun'][0] + ", " + df['province'][0] + ", " + df['region'][0]

                sql_assignedsex = """ SELECT assignedsex_name FROM utilities.assignedsex
                WHERE assignedsex_id = %s;""" % (assignedsex)

                assignedsex_values = []
                assignedsex_cols = ['assignedsex_name']
                assignedsex_df = db.querydatafromdatabase(sql_assignedsex, assignedsex_values, assignedsex_cols)
                assignedsex_label = assignedsex_df.iloc[0,0]

                if mname == None: mname = ""
                
                type_info = []

                modal_content = [
                    html.H5("🙋 Basic information"),
                    html.B("Name : "), "%s, %s %s" % (lname, fname, mname), html.Br(),
                    html.B("ID number: "), user_id, html.Br(),
                    html.B("Username: "), username, html.Br(),
                    html.B("Date of birth: "), birthdate, html.Br(),
                    html.B("Assigned sex at birth: "), assignedsex_label, html.Br(),
                    html.Br(),

                    html.H5("📲 Contact information"),
                    html.B("Contact number: "), contactnum, html.Br(),
                    html.B("Email address: "), email, html.Br(),
                    html.Br(),

                    html.H5("📌 Present address"),
                    present_address,
                    html.Br(), html.Br(),

                    html.H5("🏠 Permanent address"),
                    permanent_address,
                    html.Br(), html.Br(),
                ]

                if pronouns or honorific or livedname:
                    modal_content += [html.H5("🫶 Optional information")]
                    if honorific:
                        modal_content += [
                            html.B("Preferred honorific: "), honorific, html.Br()
                        ]
                    if livedname:
                        modal_content += [
                            html.B("Lived name: "), livedname, html.Br()
                        ]
                    if pronouns:
                        modal_content += [
                            html.B("Pronouns: "), pronouns, html.Br()
                        ]
                    modal_content += [html.Br()]
                
                if user_type == 1:
                    sql = """ SELECT us_c.college_name AS college, us_d.degree_name AS degree
                    FROM utilities.degreeprogram AS us_d
                    INNER JOIN utilities.college AS us_c ON us_d.college_id = us_c.college_id
                    WHERE us_d.college_id = %s AND us_d.degree_id = %s;"""
                    values = [student_college, degree]
                    cols = ['college', 'degree']
                    df = db.querydatafromdatabase(sql, values, cols)
                    college_label = df['college'][0]
                    degree_label = df['degree'][0]

                    sql = """ SELECT year_level FROM utilities.yearlevel
                    WHERE year_id = %s;""" % (year_level)
                    values = []
                    cols = ['year_level']
                    df = db.querydatafromdatabase(sql, values, cols)
                    year_label = df.iloc[0,0]

                    modal_content += [
                        html.H5("🧑‍🎓 Student information"),
                        html.B("College: "), college_label, html.Br(),
                        html.B("Degree program: "), degree_label, html.Br(),
                        html.B("Year level: "), year_label, html.Br(),
                        html.Br()
                    ]
                elif user_type == 2:
                    sql = """ SELECT college_name FROM utilities.college WHERE college_id = %s;"""
                    values = [faculty_college]
                    cols = ['college_name']
                    df = db.querydatafromdatabase(sql, values, cols)
                    college_label = df.iloc[0,0]

                    sql = """ SELECT accesstype_name FROM utilities.accesstype
                    WHERE accesstype_id = %s;""" % (faculty_accesstype)
                    values = []
                    cols = ['accesstype_name']
                    df = db.querydatafromdatabase(sql, values, cols)
                    accesstype_label = df.iloc[0,0]

                    modal_content += [
                        html.H5("🧑‍🏫 Faculty information"),
                        html.B("College: "), college_label, html.Br(),
                        html.B("Designation: "), faculty_desig, html.Br(),
                        html.B("Access type: "), accesstype_label, html.Br(),
                        html.Br()
                    ]
                elif user_type == 3:
                    sql = """ SELECT office_name FROM utilities.office WHERE office_id = %s;"""
                    values = [office]
                    cols = ['office_name']
                    df = db.querydatafromdatabase(sql, values, cols)
                    office_label = df.iloc[0,0]

                    sql = """ SELECT accesstype_name FROM utilities.accesstype WHERE accesstype_id = %s;"""
                    values = [staff_accesstype]
                    cols = ['accesstype_name']
                    df = db.querydatafromdatabase(sql, values, cols)
                    accesstype_label = df.iloc[0,0]

                    modal_content += [
                        html.H5("🧑‍💼 Staff information"),
                        html.B("Office: "), office_label, html.Br(),
                        html.B("Designation: "), staff_desig, html.Br(),
                        html.B("Access type: "), accesstype_label, html.Br(),
                        html.Br()
                    ]

                modal_content += [
                    html.Hr(),
                    dbc.Alert(id = 'confirm_alert', is_open = False),
                    html.H6("To confirm your information, please create your password"),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Input(type = 'password', id = 'user_password', placeholder = 'Password' )
                                ]
                            )
                        ], className = 'mb-3'
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Input(type = 'password', id = 'confirm_password', placeholder = 'Confirm password' )
                                ]
                            )
                        ], className = 'mb-3'
                    ),
                ]
            return [alert_color, alert_text, alert_open, modal_open, modal_content]
        else: raise PreventUpdate
    else: raise PreventUpdate

@app.callback(
    [
        Output('confirm_alert', 'color'),
        Output('confirm_alert', 'children'),
        Output('confirm_alert', 'is_open'),
    ],
    [
        Input('confirm_btn', 'n_clicks'),
    ],
    [
        State('user_password', 'value'),
        State('confirm_password', 'value')
    ]
)

def password_check(btn, password, confirm):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'confirm_btn' and btn:
            alert_color = ''
            alert_text = ''
            alert_open = False
            if (password == None or password == '') and (confirm == None or confirm == ''):
                alert_color = 'warning'
                alert_open = True
                alert_text = "Please create your password."
            elif password == '' and confirm:
                alert_color = 'warning'
                alert_open = True
                alert_text = "Please create your password."
            elif password and confirm == '':
                alert_color = 'warning'
                alert_open = True
                alert_text = "Please confirm your password."
            elif password != confirm:
                alert_color = 'danger'
                alert_open = True
                alert_text = "Passwords do not match."
            return [alert_color, alert_text, alert_open]
        else: raise PreventUpdate
    else: raise PreventUpdate

layout = html.Div(
    [
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H1(['Register User'])
                            ],
                            id = 'profile_header'
                        ),
                        html.Hr(),
                        dbc.Form(
                            [
                                html.Div(
                                    [
                                        dbc.Alert(id = 'register_alert', is_open = False),
                                        dbc.Row(
                                            [
                                                dbc.Label ("User type", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(id = 'usertype_id'), width = 3
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
                                        html.Div(
                                            [
                                                #html.Hr(),
                                                #html.H3("Student Information"),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("College", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'student_college_id'
                                                            ), width = 9
                                                        )
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Degree Program", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'degree_id',
                                                                disabled = True
                                                            ), width = 9
                                                        ),
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Year level", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'year_id'
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
                                                                id = 'student_accesstype_id',
                                                                value = 1,
                                                                disabled = True
                                                            ), width = 3
                                                        )
                                                    ],
                                                    id = 'studentid_block',
                                                    style = {'display' : 'none'},
                                                    className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
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
                                                    style = {'display' : 'none'},
                                                    className = 'mb-3'
                                                )
                                            ],
                                            id = 'student_form',
                                            style = {'display' : 'none'}
                                        ),
                                        html.Div(
                                            [
                                                #html.Hr(),
                                                #html.H3("Faculty Information"),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("College", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'faculty_college_id'
                                                            ), width = 9
                                                        )
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Designation", width = 2),
                                                        dbc.Col(
                                                            dbc.Input(
                                                                type = 'text',
                                                                id = 'faculty_desig',
                                                                placeholder = 'e.g. Instructor I, Professor II'
                                                            ),
                                                            width = 9
                                                        )
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Access type", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'faculty_accesstype_id',
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
                                            ],
                                            id = 'faculty_form',
                                            style = {'display' : 'none'}
                                        ),
                                        html.Div(
                                            [
                                                #html.Hr(),
                                                #html.H3("Staff Information"),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Office", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'office_id'
                                                            ), width = 9
                                                        )
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Designation", width = 2),
                                                        dbc.Col(
                                                            dbc.Input(
                                                                type = 'text',
                                                                id = 'staff_desig',
                                                                placeholder = 'e.g. Registrar I, Librarian I'
                                                            ),
                                                            width = 9
                                                        )
                                                    ], className = 'mb-3'
                                                ),
                                                dbc.Row(
                                                    [
                                                        dbc.Label("Access type", width = 2),
                                                        dbc.Col(
                                                            dcc.Dropdown(
                                                                id = 'staff_accesstype_id',
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
                                            ],
                                            id = 'staff_form',
                                            style = {'display' : 'none'}
                                        ),
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
                                        dbc.Row(
                                            [
                                                dbc.Label("Province", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'present_province_id', 
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("City/Municipality", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'present_citymun_id', 
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Barangay", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'present_brgy_id', 
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Street address", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        id = 'present_street',
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
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
                                        dbc.Row(
                                            [
                                                dbc.Label("Province", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'permanent_province_id',
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("City/Municipality", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'permanent_citymun_id', 
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Barangay", width = 2),
                                                dbc.Col(
                                                    dcc.Dropdown(
                                                        id = 'permanent_brgy_id',
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Label("Street address", width = 2),
                                                dbc.Col(
                                                    dbc.Input(
                                                        id = 'permanent_street',
                                                        disabled = True
                                                    ), width = 9
                                                )
                                            ], className = 'mb-3'
                                        ),
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
                    id = 'register_modalbody'
                ),
                dbc.ModalFooter(
                    [
                        dbc.Button(
                            "Confirm", id = 'confirm_btn'
                        )
                    ]
                )
            ],
            centered = True,
            id = 'register_confirmationmodal',
            backdrop = 'static'
        )
    ]
)