from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime, timedelta
import pytz
import hashlib
import math

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

# Callback for generating active loans
@app.callback(
    [
        Output('active_loans', 'children')
    ],
    [
        Input('url', 'pathname')
    ]
)

def generate_loans(pathname):
    if pathname == '/circulation/loans':
        tables = []
        sql = """SELECT c.borrow_id AS id, c.accession_num AS accession_num,
            r_t.resource_title AS title, r_t.title_id AS title_id, r_c.library_id AS library_id,
            r_l.library_name AS library, c.user_id AS user_id, u.user_lname AS lname, u.user_fname AS fname,
            u.user_mname AS mname, u.user_livedname AS livedname,
            TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bordate,
            TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS retdate,
            c.borrow_date AS raw_bordate,
            c.return_date AS raw_retdate
            FROM cartblock.borrowcart AS c
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            LEFT JOIN userblock.registereduser AS u ON c.user_id = u.user_id
            LEFT JOIN utilities.libraries AS r_l ON r_c.library_id = r_l.library_id
            WHERE r_c.circstatus_id = 2 AND c.cart_returned = FALSE;
        """
        values = []
        cols = ['id', 'Accession #', 'Title', 'Title ID', 'Library ID', 'Library', 'user_id', 'lname', 'fname', 'mname', 'livedname', 'Borrowed on', 'Return on', 'bordate', 'retdate']
        df = db.querydatafromdatabase(sql, values, cols)

        # Render user names
        lname = ''
        fname = ''
        mname = ''
        user_name = []
        users = []
        # Status badges
        statuses = []
        for i in df.index:
            badge_color = 'secondary'
            badge_text = 'Borrowed'
            # Rewriting titles as links
            df.loc[i, 'Title'] = html.A(df['Title'][i], href = '/resource/record?id=%s' % df['Title ID'][i])
            # Combine user names into single line
            lname = df['lname'][i]
            if df['livedname'][i] != None: fname = df['livedname'][i]
            else: fname = df['fname'][i]
            if df['mname'][i] != None: mname = " " + df['mname'][i][0] + "."
            user_name.append("%s, %s%s" % (lname, fname, mname))
            # Determine status
            remaining_time = (df['retdate'][i] - datetime.now(pytz.timezone('Asia/Manila'))).total_seconds()/(60*60)
            #print(remaining_time)
            if remaining_time <= 1 and remaining_time >= 0:
                badge_color = 'warning'
            elif remaining_time < 0:
                badge_color = 'danger'
                badge_text = "Overdue"
            # Append user names, statuses, and buttons for returning
            users.append(html.A(["%s, %s%s" % (lname, fname, mname)], href = '/user/profile?mode=view&id=%s' %df['user_id'][i]))
            statuses.append(dbc.Badge(badge_text, color = badge_color))
        df.insert(2, "User", users, True)
        df.insert(5, "Status", statuses, True)
        df.insert(6, "Full name", user_name, True)
        if df.shape[0] > 0:
            df = df.groupby('user_id')
            for name, group in df:
                borrow_id = group['id'].drop_duplicates().iloc[0]
                name = group['Full name'].drop_duplicates().iloc[0] #group['User'].drop_duplicates().iloc[0]
                group = group[['Accession #', 'Title', 'Library', 'Borrowed on', 'Return on', 'Status']].sort_values(by = ['Borrowed on'])
                tables.append(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            [
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Table.from_dataframe(group, hover = True, size = 'sm')
                                    )
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Button(
                                            "Return resources",
                                            id = {'type' : 'return_btn', 'index' : int(borrow_id)},
                                            style = {'width' : '100%'}
                                        )
                                    )
                                )
                            ],
                            title = name
                        ), className = 'mb-3'
                    )
                )
        else:
            tables.append(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            "There are no active loans at the moment.",
                            title = "Loans"
                        ), className = 'mb-3'
                    )
                )
        return [tables]
    else: raise PreventUpdate

# Callback for confirming return
@app.callback(
    [
        Output('confirmreturn_modal', 'is_open'),
        Output('confirmreturn_content', 'children'),
        Output('returner_id', 'data'),
        Output('borrow_id', 'data'),
        Output('retcon_alert', 'children'),
        Output('retcon_alert', 'color'),
        Output('confirmreturn_text', 'children'),
        Output('is_penalty', 'data'),
        Output('penalty_peso', 'data'),
        Output('penalty_mins', 'data'),
        Output('penalty_select', 'style'),
        Output('returner_eligibility', 'data')
    ],
    [
        Input('url', 'pathname'),
        Input({'type' : 'return_btn', 'index' : ALL}, 'n_clicks')
    ],
    prevent_initial_call = True
)

def confirm_return(pathname, btn):
    if pathname == '/circulation/loans':
        ctx = dash.callback_context
        if ctx.triggered[-1]['value'] == None: raise PreventUpdate
        else:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0].split(',')[1].split(':')[1][1:-2]
            if eventid == 'return_btn' and btn:
                is_open = True
                content = []
                is_penalty = False
                penalty_peso = 0
                penalty_mins = 0
                borrow_id = int(ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1])
                #user_id = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1].split("&")[1][:-1]
                #accession_num = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1].split("&")[2][:-1]
                confirmreturn_text = ["Please enter your password to confirm the return of this resource."]

                sql = """SELECT c.accession_num AS accession_num, c.user_id AS user_id, u.user_lname AS lname, u.user_fname AS fname, u.user_mname AS mname, u.user_livedname AS livedname, u.borrowstatus_id AS status,
                    TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bordate,
                    TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS retdate,
                    c.borrow_date AS raw_bordate, c.return_date AS raw_retdate,
                    r.resource_title AS title, r.title_id AS id, r_t.resourcetype_name AS type, r_c.copy_callnum AS callnum,
                    r_l.language_name AS language, r_p.publisher_name AS publisher, r.copyright_date AS date,
                    r.resource_edition AS edition, r_col.collection_name AS collection, l.library_name AS library
                    FROM cartblock.borrowcart AS c
                    LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
                    LEFT JOIN resourceblock.resourceset AS r_s ON r_c.resource_id = r_s.resource_id
                    LEFT JOIN resourceblock.resourcetitles AS r ON r_s.title_id = r.title_id
                    LEFT JOIN utilities.resourcetype AS r_t ON r.resourcetype_id = r_t.resourcetype_id
                    LEFT JOIN utilities.languages AS r_l ON r.language_id = r_l.language_id
                    LEFT JOIN resourceblock.publishers AS r_p ON r.publisher_id = r_p.publisher_id
                    LEFT JOIN resourceblock.collections AS r_col ON r.collection_id = r_col.collection_id
                    LEFT JOIN utilities.libraries AS l ON r_c.library_id = l.library_id
                    LEFT JOIN userblock.registereduser AS u ON c.user_id = u.user_id
                    WHERE c.borrow_id = %s;"""
                values = [borrow_id]
                cols = [
                    'Accession #', 'user_id', 'lname', 'fname', 'mname', 'livedname', 'status', 'bordate', 'retdate', 'raw_bordate', 'raw_retdate',
                    'Title', 'Title ID', 'Type', 'Call #', 'Language', 'Publisher', 'Copyright date', 'Edition',
                    'Collection', 'Library'
                ]
                df = db.querydatafromdatabase(sql, values, cols)
                title_id = df['Title ID'][0]
                user_id = df['user_id'][0]

                lname = ''
                fname = ''
                mname = ''
                lname = df['lname'][0]
                if df['livedname'][0]: fname = df['livedname'][0]
                else: fname = df['fname'][0]
                if df['mname'][0]: mname = " " + df['mname'][0][0] + "."
                name = "%s, %s%s" % (lname, fname, mname)
                content.append(
                    html.P(
                        [
                            "Confirm the return of the following resource by ",
                            html.A(html.B(name), href = '/user/profile?mode=view&id=%s' % user_id),
                            " (ID number %s):" % user_id
                        ], className = 'mb-0'
                    )
                )

                card_content = []
                table = df[['Accession #', 'Call #', 'Library', 'Title', 'Type', 'Publisher', 'Copyright date', 'Edition']]
                #table.insert(0, "Information", [html.B('Call number'), html.B('Language'), html.B('Publisher'), html.B('Copyright date'), html.B('Edition'), html.B('Collection'), html.B('Library')], True)
                #table = table.rename(columns={'Information' : '', 0 : ''})
                card_content += [
                    dbc.Table.from_dataframe(
                        table, hover = True, size = 'sm'#, className = 'mb-3'
                    ),
                ]
                content.append(dbc.Card(dbc.CardBody(card_content), className = 'my-3 p-3'))

                # Penalty determination
                sql = """SELECT penalty_value AS penalty, penalty_type AS type
                FROM utilities.penaltyperday
                ORDER BY penalty_id ASC ;"""
                values = []
                cols = ['penalty', 'type']
                df_penalty = db.querydatafromdatabase(sql, values, cols)

                eligiblity = True

                retcon_text = ["These resource are being returned ", html.B("on time"), "."]
                retcon_color = 'success'
                remaining_time = (df['raw_retdate'][0] - datetime.now(pytz.timezone('Asia/Manila'))).total_seconds()/(60*60)
                penalty_style = {'display' : 'none'}
                if remaining_time < 0:
                    penalty = math.ceil(abs(remaining_time/24))
                    is_penalty = True
                    penalty_peso = df_penalty['penalty'][0]*penalty*df.shape[0]
                    penalty_mins = df_penalty['penalty'][1]*penalty*df.shape[0]
                    retcon_text = [
                        "These resources were due for return on %s and are already " % df['retdate'][0], html.B("OVERDUE"), ".",
                        " A payment of ", html.B("₱%s OR %s minutes of community service" % (penalty_peso, penalty_mins)),
                        " is required to clear this penalty."
                    ]
                    retcon_color = 'danger'
                    eligiblity = False
                    confirmreturn_text += [
                            " ", html.B("Make sure that any penalties incurred have already been paid/rendered beforehand.")
                    ]
                    penalty_style = {'display' : 'block'}
                return [is_open, content, user_id, borrow_id, retcon_text, retcon_color, confirmreturn_text, is_penalty, penalty_peso, penalty_mins, penalty_style, eligiblity]
            else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for authorizing returns
@app.callback(
    [
        Output('confirmreturn_alert', 'color'),
        Output('confirmreturn_alert', 'children'),
        Output('confirmreturn_alert', 'is_open'),
    ],
    [
        Input('confirmreturn_btn', 'n_clicks')
    ],
    [
        State('return_password', 'value'),
        State('currentuserid', 'data'),
        State('returner_id', 'data'),
        State('borrow_id', 'data'),
        State('is_penalty', 'data'),
        State('penalty_peso', 'data'),
        State('penalty_mins', 'data'),
        State('penalty_options', 'value'),
        State('returner_eligibility', 'data')
    ]
)

def authorize_returns(btn, password, user_id, returner_id, borrow_id,
                      is_penalty, penalty_peso, penalty_mins, penalty_option,
                      eligiblity):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'confirmreturn_btn' and btn:
            color = 'success'
            text = 'Resource successfully returned.'
            is_open = True
            if not password or password == '':
                color = 'warning'
                text = 'Please enter your password.'
            else:
                encrypt_string = lambda string: hashlib.sha256(string.encode('utf-8')).hexdigest()
                sql = """SELECT user_id AS id
                    FROM userblock.registereduser
                    WHERE user_id = %s AND user_password = %s;"""
                values = [user_id, encrypt_string(password)]
                cols = ['id']
                df = db.querydatafromdatabase(sql, values, cols)
                if df.shape[0] == 0:
                    color = 'danger'
                    text = "Incorrect password"
                    is_open = True
                else:
                    if not eligiblity and penalty_option == None:
                        color = 'warning'
                        text = 'Please select a method to clear the penalty.'
                    else:
                        sql = """SELECT accession_num FROM cartblock.borrowcart WHERE borrow_id = %s;"""
                        values = [borrow_id]
                        cols = ['accession_num']
                        accession_nums = tuple(db.querydatafromdatabase(sql, values, cols)['accession_num'].values.tolist())
                        penalty_p = 0
                        penalty_m = 0
                        sql = """UPDATE resourceblock.resourcecopy
                            SET circstatus_id = 1
                            WHERE accession_num IN %s;
                            
                            UPDATE cartblock.borrowcart
                            SET return_date = %s, cart_returned = %s, overdue_fine = %s, overdue_mins = %s"""
                        values = [accession_nums, datetime.now(pytz.timezone('Asia/Manila')), True]
                        if is_penalty:
                            if penalty_option == 0:
                                penalty_p = penalty_peso/len(accession_nums)
                            elif penalty_option == 1:
                                penalty_m = penalty_mins/len(accession_nums)
                        values += [penalty_p, penalty_m]
                        sql += """ WHERE borrow_id = %s;
                            UPDATE userblock.registereduser
                            SET borrowstatus_id = 1
                            WHERE user_id = %s;"""
                        values += [borrow_id, returner_id]
                        db.modifydatabase(sql, values)
            return [color, text, is_open]
        else: raise PreventUpdate
    else: raise PreventUpdate

layout = html.Div(
    [
        dcc.Store(id = 'return_id', storage_type = 'memory'),
        dcc.Store(id = 'returner_id', storage_type = 'memory'),
        dcc.Store(id = 'borrow_id', storage_type = 'memory'),
        dcc.Store(id = 'is_penalty', data = False, storage_type = 'memory'),
        dcc.Store(id = 'penalty_peso', data = 0, storage_type = 'memory'),
        dcc.Store(id = 'penalty_mins', data = 0, storage_type = 'memory'),
        dcc.Store(id = 'returner_eligibility', storage_type = 'memory'),
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.H1("Active loans"),
                        html.Hr(),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'borrow_alert',
                                    dismissable = True,
                                    duration = 5000,
                                    is_open = False
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    id = 'active_loans'
                                )
                            )
                        )
                    ]
                )
            ]
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirm return")),
                dbc.ModalBody(
                    [
                        html.Div(id = 'confirmreturn_content'),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'retcon_alert',
                                    dismissable = False,
                                    is_open = True
                                ), #lg = 6
                            ), justify = 'center'
                        ),
                        html.Div(
                            [
                                dbc.Row(
                                    dbc.Col(
                                        dbc.Label("Select the penalty to clear:"),
                                        width = 'auto'
                                    ), justify = 'center'
                                ),
                                dbc.Row(
                                    dbc.Col(
                                        [
                                            dbc.RadioItems(
                                                options = [
                                                    {'label' : 'Fine (Peso/₱)', 'value' : 0},
                                                    {'label' : 'Community service (minutes)', 'value' : 1}
                                                ],
                                                id = 'penalty_options',
                                                inline = True
                                            )
                                        ], width = 'auto'
                                    ),
                                    className = 'mb-3',
                                    justify = 'center'
                                )
                            ],
                            id = 'penalty_select',
                            style = {'display' : 'none'}
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Span(id = 'confirmreturn_text'),
                                lg = 8
                            ),
                            className = 'mb-3',
                            justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'confirmreturn_alert',
                                    dismissable = True,
                                    is_open = False
                                ), lg = 6
                            ), justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Input(
                                    type = 'password',
                                    id = 'return_password',
                                    placeholder = 'Password'
                                ),
                                lg = 6,
                                className = 'mb-3'
                            ),
                            justify = 'center'
                        )
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Confirm", id = 'confirmreturn_btn')
                )
            ],
            id = 'confirmreturn_modal',
            size = 'lg',
            scrollable = True,
            className = 'p-3'
        )
    ]
)