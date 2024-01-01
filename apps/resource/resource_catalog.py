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

# Callback for populating dropdown menus
@app.callback(
    [
        Output('resourcetype_id', 'options'),
        Output('subj_tier1_id', 'options'),
        Output('resource_authors', 'options'),
        Output('language_id', 'options'),
        Output('publisher_id', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('newauthor_btn', 'n_clicks'),
        Input('newpublisher_btn', 'n_clicks')
    ],
    #[
    #    Input('page_mode', 'data'),
    #    Input('view_id', 'data')
    #]
)

def populate_dropdowns(pathname, author_btn, publisher_btn):
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
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['label'])
        authors = df.to_dict('records')

        # Languages
        sql = """SELECT language_name as label, language_id as value
            FROM utilities.languages;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        languages = df.to_dict('records')

        # Publishers
        sql = """SELECT CONCAT(publisher_name, ' (', publisher_loc, ')') as label, publisher_id as value
            FROM resourceblock.publishers;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['label'])
        publishers = df.to_dict('records')
        return [resourcetype, subjecttier1, authors, languages, publishers]
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
        Input('copyright_date', 'date')
    ]
)

def generate_callnum(pathname, t1, t2, t3, res_authors, date):
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
        if res_authors:
            authors = []
            if res_authors:
                #print(res_authors)
                None
        if date:
            L3 = date.split("-")[0]
        if L1 != 'AAA' or L2 != 'BBBB' or L3 != 'YYYY':
            return["%s-%s-%s" % (L1, L2, L3)]
        else: return [None]
    else: raise PreventUpdate

# Callback for registering new author
@app.callback(
    [
        Output('newauthor_alert', 'children'),
        Output('newauthor_alert', 'color'),
        Output('newauthor_alert', 'is_open'),
        Output('author_lname', 'value'),
        Output('author_fname', 'value'),
        Output('author_mname', 'value'),
        #Output('resource_authors', 'value'),
    ],
    [
        Input('url', 'pathname'),
        Input('newauthor_btn', 'n_clicks')
    ],
    [
        State('author_lname', 'value'),
        State('author_fname', 'value'),
        State('author_mname', 'value'),
        #State('resource_authors', 'value'),
    ]
)

def register_author(pathname, btn, lname, fname, mname):
    if pathname == '/resource/catalog':
        ctx = dash.callback_context
        if ctx.triggered:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0]
            if eventid == 'newauthor_btn' and btn:
                if lname == '' or lname == None: lname = None
                if fname == '' or fname == None: fname = None
                if mname == '' or mname == None: mname = None
                alert_text = ''
                alert_color = ''
                alert_open = True
                if lname and fname:
                    sql = """SELECT author_id AS id
                        FROM resourceblock.authors
                        WHERE author_lname = %s AND author_fname = %s AND author_mname = %s;"""
                    values = [lname, fname, mname]
                    cols = ['id']
                    df = db.querydatafromdatabase(sql, values, cols)
                    print(sql)
                    print(df)
                    if not df.empty:
                        alert_text = "This author already exists. Please select them in the dropdown menu above."
                        alert_color = 'danger'
                    else:
                        sql = """INSERT INTO resourceblock.authors(author_lname, author_fname, author_mname)
                            VALUES(%s, %s, %s);"""
                        values = [lname, fname, mname]
                        db.modifydatabase(sql, values)
                        alert_text = "New author successfully registered. Please select them in the dropdown menu above."
                        alert_color = 'success'
                        lname = None
                        fname = None
                        mname = None
                else:
                    if lname == None or lname == '': alert_text = "Please input the author's last name."
                    if fname == None or fname == '': alert_text = "Please input the author's first name."
                    if (lname == None or lname == '') and (fname == None or fname == ''): alert_text = "Please input the author's first and last names."
                    alert_color = 'warning'
                return [alert_text, alert_color, alert_open, lname, fname, mname]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for registering new publisher
@app.callback(
    [
        Output('newpublisher_alert', 'children'),
        Output('newpublisher_alert', 'color'),
        Output('newpublisher_alert', 'is_open')
    ],
    [
        Input('url', 'pathname'),
        Input('newpublisher_btn', 'n_clicks')
    ],
    [
        State('publisher_name', 'value'),
        State('publisher_loc', 'value')
    ]
)

def register_author(pathname, btn, name, loc):
    if pathname == '/resource/catalog':
        ctx = dash.callback_context
        if ctx.triggered:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0]
            if eventid == 'newpublisher_btn' and btn:
                if name == '' or name == None: name = None
                if loc == '' or loc == None: loc = None
                alert_text = ''
                alert_color = ''
                alert_open = True
                if name:
                    sql = """SELECT publisher_id AS id
                        FROM resourceblock.publishers
                        WHERE publisher_name = %s AND publisher_loc = %s;"""
                    values = [name, loc]
                    cols = ['id']
                    df = db.querydatafromdatabase(sql, values, cols)
                    #print(df.empty)
                    if not df.empty:
                        alert_text = "This publisher already exists. Please select them in the dropdown menu above."
                        alert_color = 'danger'
                        #alert_open = True
                    else:
                        sql = """INSERT INTO resourceblock.publishers(publisher_name, publisher_loc)
                            VALUES(%s, %s);"""
                        values = [name, loc]
                        db.modifydatabase(sql, values)
                        alert_text = "New publisher successfully registered. Please select them in the dropdown menu above."
                        alert_color = 'success'
                        #alert_open = True
                elif name == None or name == '':
                    alert_text = "Please input the publisher's name."
                    alert_color = 'warning'
                    #alert_open = True
                return [alert_text, alert_color, alert_open]
        else: raise PreventUpdate
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
                            dbc.Alert(
                                id = 'register_alert',
                                is_open = False,
                                dismissable = True,
                                duration = 5000
                                ),
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
                                            id = 'resourcetype_id',
                                            placeholder = 'Select resource type...'
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
                                    is_open = False,
                                    duration = 5000
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
                                    ["""If the authors of this resource are not found above, you can register them here first."""]
                                ),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    #dbc.Label("Author name", width = 2),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'author_lname',
                                            placeholder = 'Surname'
                                        ), width = 3 #9
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'author_fname',
                                            placeholder = 'First name'
                                        ), width = 3 #9
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'author_mname',
                                            placeholder = 'Middle name'
                                        ), width = 3 #9
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Register",
                                            id = 'newauthor_btn',
                                            style = {'width' : '100%'}
                                        ), width = 2
                                    )
                                ], className = 'mb-3'
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Alert(
                                        id = 'newauthor_alert',
                                        is_open = False,
                                        dismissable = True,
                                        duration = 5000
                                    ),
                                    width = 11
                                ),
                                className = 'mb-3'
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
                                    dbc.Label(
                                        "Edition number",
                                        width = 3),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'resource_edition',
                                            placeholder = 'Example: 1, 2, 3',
                                        ), width = 3
                                    ),
                                ], className = 'mb-3'
                            ),
                            dbc.Row(
                                [
                                    dbc.Label(
                                        "Language",
                                        width = 2),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'language_id',
                                            placeholder = 'Select language...'
                                        ), width = 3
                                    ),
                                    dbc.Label(
                                        "Collection",
                                        width = 3),
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'collection_id',
                                            placeholder = 'Select collection...'
                                        ), width = 3
                                    ),
                                ], className = 'mb-3'
                            ),
                            html.H5("Publisher"),
                            dbc.Col(
                                html.P(
                                    """If the publisher of this resource is already registered in LÁRA,
                                    you can select them in the dropdown menu below."""
                                ),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dcc.Dropdown(
                                            id = 'publisher_id',
                                            placeholder = 'Publisher',
                                        ), width = 11 #9
                                    ),
                                ], className = 'mb-3'
                            ),
                            dbc.Col(
                                html.P(
                                    ["""If the publisher of this resource is not found above, you can register them here first."""]
                                ),
                                width = 11
                            ),
                            dbc.Row(
                                [
                                    #dbc.Label("Publisher information", width = 2),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'publisher_name',
                                            placeholder = 'Publisher name'
                                        ), width = 6 #9
                                    ),
                                    dbc.Col(
                                        dbc.Input(
                                            type = 'text',
                                            id = 'publisher_loc',
                                            placeholder = 'Publisher city/state/country'
                                        ), width = 3 #9
                                    ),
                                    dbc.Col(
                                        dbc.Button(
                                            "Register",
                                            id = 'newpublisher_btn',
                                            style = {'width' : '100%'}
                                        ), width = 2
                                    )
                                ], className = 'mb-3'
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Alert(
                                        id = 'newpublisher_alert',
                                        is_open = False,
                                        dismissable = True,
                                        duration = 5000
                                    ),
                                    width = 11
                                ),
                                className = 'mb-3'
                            ),
                        ],
                        id = 'resource_catalog'
                    )
                ]
            )
        ]
    )
]