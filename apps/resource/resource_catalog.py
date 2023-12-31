from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from urllib.parse import urlparse, parse_qs

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

import hashlib

# Callback for generating call number
@app.callback(
    [
        Output('call_num', 'value')
    ],
    [
        Input('url', 'pathname'),
        Input('subj_tier1_id', 'value'),
        Input('subj_tier2_id', 'value'),
        Input('subj_tier3_id', 'value'),
        Input('resource_authors', 'value'),
        Input('new_authors', 'value'),
        Input('copyright_date', 'date')
    ]
)

def generate_callnum(pathname, t1, t2, t3, res_authors, new_authors, date):
    if pathname == '/resource/catalog':
        L1 = 'AAA'
        L2 = 'BBBB'
        L3 = 'YYYY'
        if t1 != None and t1 >= 0:
            L1 = str(t1*100).zfill(3)
            if t2 != None and t2 >= 0:
                L1 = str(t1*100 + t2*10).zfill(3)
                if t3 != None and t3 >= 0:
                    L1 = str(t1*100 + t2*10 + t3).zfill(3)
        if res_authors or new_authors:
            authors = []
            if res_authors: print(res_authors)
            if new_authors:
                #print(new_authors.split(";"))
                None
        if date:
            L3 = date.split("-")[0]
        if L1 != 'AAA' or L2 != 'BBBB' or L3 != 'YYYY':
            return["%s-%s-%s" % (L1, L2, L3)]
        else: return [None]
    else: raise PreventUpdate

# Callback for populating dropdown menus
@app.callback(
    [
        Output('resourcetype_id', 'options'),
        Output('subj_tier1_id', 'options'),
        Output('resource_authors', 'options')
    ],
    [
        Input('url', 'pathname')
    ],
    #[
    #    Input('page_mode', 'data'),
    #    Input('view_id', 'data')
    #]
)

def populate_dropdowns(pathname):
    if pathname == '/resource/catalog':
        # Resource types
        sql = """SELECT resourcetype_name as label, resourcetype_id as value
            FROM utilities.resourcetype;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        resourcetype = df.to_dict('records')

        # Subject tier 1
        sql = """SELECT CONCAT(TO_CHAR(subj_tier1_id*100, '000'), ' ', subj_tier1_name) as label, subj_tier1_id as value
            FROM utilities.subjecttier1 WHERE subj_tier1_name IS NOT NULL;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        subjecttier1 = df.to_dict('records')

        # Authors
        sql = """SELECT CONCAT(author_lname, ', ', author_fname, ' ', author_mname) as label, author_id as value
            FROM resourceblock.authors;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        authors = df.to_dict('records')
        return [resourcetype, subjecttier1, authors]
    else: raise PreventUpdate

# Callback for populating Level 2 class
@app.callback(
    [
        Output('subj_tier2_id', 'options'),
        Output('subj_tier2_id', 'value'),
        Output('subj_tier2_id', 'disabled'),
    ],
    [
        Input('url', 'pathname'),
        Input('subj_tier1_id', 'value')
    ]
)

def populate_subjecttier2(pathname, t1):
    if pathname == '/resource/catalog':
        options = {}
        disabled = True
        if t1 != None and t1 >= 0:
            sql = """SELECT
                    CONCAT(TO_CHAR(subj_tier1_id*100 + subj_tier2_id*10, '000'), ' ', subj_tier2_name) as label,
                    subj_tier2_id as value
                    FROM utilities.subjecttier2
                    WHERE subj_tier1_id = %s AND subj_tier2_name IS NOT NULL;"""
            values = [t1]
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
            options = df.to_dict('records')
            disabled = False
        return [options, None, disabled]
    else: raise PreventUpdate

# Callback for populating Level 3 class
@app.callback(
    [
        Output('subj_tier3_id', 'options'),
        Output('subj_tier3_id', 'value'),
        Output('subj_tier3_id', 'disabled'),
    ],
    [
        Input('url', 'pathname'),
        Input('subj_tier1_id', 'value'),
        Input('subj_tier2_id', 'value')
    ]
)

def populate_subjecttier3(pathname, t1, t2):
    if pathname == '/resource/catalog':
        options = {}
        disabled = True
        if t1 != None and t1 >= 0 and t2 != None and t2 >= 0:
            sql = """SELECT CONCAT(TO_CHAR(subj_tier1_id*100 + subj_tier2_id*10 + subj_tier3_id, '000'), ' ', subj_tier3_name) as label, subj_tier3_id as value
                FROM utilities.subjecttier3 WHERE subj_tier1_id = %s AND subj_tier2_id = %s AND subj_tier3_name IS NOT NULL;"""
            values = [t1, t2]
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
            options = df.to_dict('records')
            disabled = False
        return [options, None, disabled]
    else: raise PreventUpdate

layout = [
    dbc.Row(
        [
            cm.sidebar,
            dbc.Col(
                [
                    html.H1("Resource record", id = 'header'),
                    html.Hr(),
                    dbc.Form(
                        [
                            dbc.Alert(id = 'register_alert', is_open = False),
                            dbc.Row(
                                [
                                    dbc.Label("Call number", width = 2),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'call_num',
                                            placeholder = 'R-AAA-BBBB-YYYY',
                                            disabled = True
                                        ), width = 3
                                    ),
                                    dbc.Label("Resource type", width = 3),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'resourcetype_id'
                                        ), width = 3
                                    )
                                ], className = 'mb-3'
                            ),
                            html.Hr(),
                            html.H3("Title Information"),
                            dbc.Col(
                                html.P("""Enter the title of this resource below."""),
                                width = 11
                            ),
                            dbc.Col(
                                dbc.Alert(
                                    "This resource already exists.",
                                    id = 'resourcetitle_alert',
                                    color = 'danger',
                                    dismissable = True,
                                    is_open = False
                                ), width = 11
                            ),
                            dbc.Col(
                                dbc.Alert(
                                    "This resource already exists.",
                                    id = 'resourcetitle_alert',
                                    color = 'danger',
                                    dismissable = True,
                                    is_open = False
                                ), width = 11
                            ),
                            dbc.Row(
                                [
                                    #dbc.Label("Title name", width = 2),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'resource_title',
                                            placeholder = 'Title name'
                                        ), width = 11 #9
                                    ),
                                ], className = 'mb-3'
                            ),
                            html.H5("Author(s)"),
                            dbc.Col(
                                html.P(
                                    """If the authors of this resource are already registered in LÁRA,
                                    you can select them in the dropdown menu below."""
                                ),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    #dbc.Label("Title name", width = 2),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            #type = 'text',
                                            id = 'resource_authors',
                                            placeholder = 'Author name(s)',
                                            multi = True
                                        ), width = 11 #9
                                    ),
                                ], className = 'mb-3'
                            ),
                            dbc.Col(
                                html.P(
                                    [
                                        """If the authors of this resource are not found above, you can register them here. Write surnames first, followed by first names,
                                        and then middle names (if any) coming in last (e.g. """,
                                        html.B('"Aguinaldo, Emilio, Famy"'), ", ", html.B('"Aquino, Maria Corazon, Cojuangco'), ", or ", html.B('"Osmeña, Sergio"'),
                                        """). Separate different authors by semicolon (e.g. """,
                                        html.B('"Aguinaldo, Emilio, Famy; Aquino, Maria Corazon, Cojuangco; Osmeña, Sergio"'),
                                        """)."""
                                    ]
                                ),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    #dbc.Label("Title name", width = 2),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'new_authors',
                                            placeholder = 'Example: de los Santos, María Clara, Alba; Eibarramendia, Juan Crisóstomo, Magsalin'
                                        ), width = 11 #9
                                    ),
                                ], className = 'mb-3'
                            ),
                            #html.Hr(),
                            html.H5("Subject class"),
                            dbc.Col(
                                html.P("""The University Library uses the Dewey Decimal System to classify different
                                        resources. Please enter the specific subject that is most appropriate for this resource according
                                        to the three levels of classification.
                                """),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Level 1 Class",
                                        id = 'subj_tier1_label',
                                        width = 2),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'subj_tier1_id'
                                        ), width = 9
                                    ),
                                    dbc.Tooltip(
                                        """Level 1 refers to the hundreds digit of the resource's subject classification. (E.g., 100, 200, 300.)""",
                                        target = 'subj_tier1_label'
                                    ),
                                ], className = 'mb-3'
                            ),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Level 2 Class",
                                        id = 'subj_tier2_label',
                                        width = 2),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'subj_tier2_id',
                                            #disabled = True
                                        ), width = 9
                                    ),
                                    dbc.Tooltip(
                                        """Level 2 refers to the tens digit of the resource's subject classification. (E.g., 110, 120, 130.)""",
                                        target = 'subj_tier2_label'
                                    ),
                                ], className = 'mb-3'
                            ),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Level 3 Class",
                                        id = 'subj_tier3_label',
                                        width = 2),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'subj_tier3_id',
                                            #disabled = True
                                        ), width = 9
                                    ),
                                    dbc.Tooltip(
                                        """Level 3 refers to the ones digit of the resource's subject classification. (E.g., 110, 111, 112.)""",
                                        target = 'subj_tier3_label'
                                    ),
                                ], className = 'mb-3'
                            ),
                            #html.Hr(),
                            #html.H5("Title Information"),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Copyright date",
                                        id = 'copyright_date_label',
                                        width = 2),
                                    dbc.Col(
                                        dcc.DatePickerSingle(
                                            id = 'copyright_date',
                                            placeholder = 'MM/DD/YYYY',
                                            month_format = 'MMM Do, YYYY',
                                            clearable = True
                                        ), width = 3
                                    ),
                                    dbc.Tooltip(
                                        """In case the resource does not have a precise copyright date
                                        (e.g. the resource was published in "January 2024" or just "2024"),
                                        set the missing day or month to "01".
                                        """,
                                        target = 'copyright_date_label'
                                    ),
                                ], className = 'mb-3'
                            ),
                        ],
                        id = 'resource_catalog'
                    )
                ]
            )
        ]
    )
]