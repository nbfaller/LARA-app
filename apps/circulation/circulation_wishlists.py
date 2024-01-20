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

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

# Callback for generating active wishlists
@app.callback(
    [
        Output('active_wishlists', 'children')
    ],
    [
        Input('url', 'pathname'),
    ]
)

def generate_wishlists(pathname):
    if pathname == '/circulation/wishlists':
        tables = []
        sql = """SELECT c.wishlist_id AS id, c.accession_num AS accession_num, r_t.resource_title AS title, r_t.title_id AS title_id, r_c.library_id AS library_id, r_l.library_name AS library,
            c.user_id AS user_id,
            u.user_lname AS lname, u.user_fname AS fname, u.user_mname AS mname, u.user_livedname AS livedname,
            TO_CHAR(c.reserve_time, 'Month dd, yyyy • HH:MI:SS AM') AS resdate,
            TO_CHAR(c.revert_time, 'Month dd, yyyy • HH:MI:SS AM') AS revdate
            FROM cartblock.wishlist AS c
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            LEFT JOIN userblock.registereduser AS u ON c.user_id = u.user_id
            LEFT JOIN utilities.libraries AS r_l ON r_c.library_id = r_l.library_id
            WHERE c.revert_time >= CURRENT_TIMESTAMP AND r_c.circstatus_id <> 2 AND u.borrowstatus_id <> 2;
        """
        values = []
        cols = ['id', 'Accession #', 'Title', 'Title ID', 'Library ID', 'Library', 'user_id', 'lname', 'fname', 'mname', 'livedname', 'Added on', 'Expires by']
        df = db.querydatafromdatabase(sql, values, cols)

        # Render user names
        lname = ''
        fname = ''
        mname = ''
        user_name = []
        users = []
        buttons = []
        for i in df.index:
            # Re-rendering titles as links
            df.loc[i, 'Title'] = html.A(
                df['Title'][i],
                href = '/resource/record?id=%s' % df['Title ID'][i]
            )
            # Re-rendering names as links
            lname = df['lname'][i]
            if df['livedname'][i]: fname = df['livedname'][i]
            else: fname = df['fname'][i]
            if df['mname'][i]: mname = " " + df['mname'][i][0] + "."
            user_name.append("%s, %s%s" % (lname, fname, mname))
            users.append(
                html.A(
                    ["%s, %s%s" % (lname, fname, mname)],
                    href = '/user/profile?mode=view&id=%s' % df['user_id'][i]
                )
            )
            buttons.append(
                html.Div(
                    dbc.Button(
                        "Remove",
                        color = 'danger',
                        size = 'sm',
                        id = {'type' : 'cancellend_btn', 'index' : int(df['id'][i])},
                        href = '#',
                        n_clicks = 0
                    )
                )
            )
        df.insert(2, "User", users, True)
        df.insert(5, "Action", buttons, True)
        #df.insert(6, "", buttons2, True)
        df.insert(6, "Full name", user_name, True)
        if df.shape[0] > 0:
            df = df.groupby('user_id')
            for name, group in df:
                accession_nums = ''
                for i in group.index:
                    accession_nums += str(group['Accession #'][i])
                    accession_nums += "-"
                accession_nums = accession_nums[:-1]
                user_id = name
                name = group['Full name'].drop_duplicates().iloc[0] #group['User'].drop_duplicates().iloc[0]
                group = group[['Accession #', 'Title', 'Library', 'Added on', 'Expires by', 'Action']].sort_values(by = ['Added on'])
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
                                    [
                                        dbc.Col(
                                            dbc.Button(
                                                "Lend resources",
                                                id = {'type' : 'lend_btn', 'index' : str(user_id) + "&" + accession_nums},
                                                style = {'width' : '100%'}
                                            ),
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "Cancel wishlist",
                                                id = {'type' : 'cancellist_btn', 'index' : str(user_id) + "&" + accession_nums},
                                                color = 'danger',
                                                style = {'width' : '100%'}
                                            ),
                                        )
                                    ],
                                    justify = 'end'
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
                            "There are no active wishlists at the moment.",
                            title = "Wishlists"
                        ), className = 'mb-3'
                    )
                )
        return [tables]
    else: raise PreventUpdate

# Callback for confirming lending
@app.callback(
    [
        Output('lendingconfirm_modal', 'is_open'),
        Output('lend_id', 'data'),
        Output('borrower_id', 'data'),
        Output('lend_information', 'children'),
        Output('borrower_name', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input({'type' : 'lend_btn', 'index' : ALL}, 'n_clicks'),
    ],
    prevent_initial_call = True
)

def confirm_lending(pathname, btn):
    if pathname == '/circulation/wishlists':
        ctx = dash.callback_context
        is_open = False
        if ctx.triggered[-1]['value'] == None: raise PreventUpdate
        else:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0].split(',')[1].split(':')[1][1:-2]
            if eventid == 'lend_btn' and btn:
                is_open = True
                accession_nums = tuple(ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split('":"')[1][:-1].split("&")[1].split("-"))
                resource_id = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1].split("&")[0][1:]
                user_id = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split('":"')[1][:-1].split("&")[0]
                info = []
                borrower_info = ''

                # Retrieving information
                sql = """SELECT r_c.accession_num AS accession_num, r.resource_title AS title, r.title_id AS id, r_t.resourcetype_name AS type, r_c.copy_callnum AS callnum,
                    r_l.language_name AS language, r_p.publisher_name AS publisher, r.copyright_date AS date,
                    r.resource_edition AS edition, r_col.collection_name AS collection, l.library_name AS library
                    FROM resourceblock.resourcecopy AS r_c
                    LEFT JOIN resourceblock.resourceset AS r_s ON r_c.resource_id = r_s.resource_id
                    LEFT JOIN resourceblock.resourcetitles AS r ON r_s.title_id = r.title_id
                    LEFT JOIN utilities.resourcetype AS r_t ON r.resourcetype_id = r_t.resourcetype_id
                    LEFT JOIN utilities.languages AS r_l ON r.language_id = r_l.language_id
                    LEFT JOIN resourceblock.publishers AS r_p ON r.publisher_id = r_p.publisher_id
                    LEFT JOIN resourceblock.collections AS r_col ON r.collection_id = r_col.collection_id
                    LEFT JOIN utilities.libraries AS l ON r_c.library_id = l.library_id
                    WHERE r_c.accession_num IN %s;"""
                values = [accession_nums]
                cols = ['Accession #', 'Title', 'Title ID', 'Type', 'Call #', 'Language', 'Publisher', 'Copyright date', 'Edition', 'Collection', 'Library']
                df = db.querydatafromdatabase(sql, values, cols)
                
                for i in df['Title'].index:
                    df.loc[i, 'Title'] = html.A(df['Title'][i], href = '/resource/record?id=%s' % df['Title ID'][i])
                
                #authors = ["by "]
                #sql = """SELECT a.author_lname AS lname, a.author_fname AS fname, a.author_mname AS mname, a.author_id AS id
                #    FROM resourceblock.resourceauthors AS r
                #    LEFT JOIN resourceblock.authors AS a ON r.author_id = a.author_id
                #    WHERE r.title_id = %s;"""
                #values = [df['Title'][0]]
                #cols =['lname', 'fname', 'mname', 'id']
                #df_authors = db.querydatafromdatabase(sql, values, cols)

                df = df[['Accession #', 'Library', 'Title', 'Type', 'Publisher', 'Copyright date', 'Edition']]
                info += [
                    dbc.Table.from_dataframe(
                        df, hover = True, size = 'sm'#, className = 'mb-3'
                    ),
                ]

                sql = """SELECT user_lname AS lname, user_fname AS fname, user_mname AS mname, user_livedname AS livedname
                    FROM userblock.registereduser
                    WHERE user_id = %s;"""
                values = [user_id]
                cols = ['lname', 'fname', 'mname', 'livedname']
                df = db.querydatafromdatabase(sql, values, cols)
                lname = ''
                fname = ''
                mname = ''
                lname = df['lname'][0]
                if df['livedname'][0]: fname = df['livedname'][0]
                else: fname = df['fname'][0]
                if df['mname'][0]: mname = " " + df['mname'][0][0] + "."
                name = "%s, %s%s" % (lname, fname, mname)
                borrower_info = html.P(["The following resources will be lent to ", html.B(html.A(["%s (%s)" % (name, user_id)], href = "/user/profile?mode=view&id=%s" % user_id)), ":"], className = 'mb-0')
                return[is_open, accession_nums, user_id, info, borrower_info]
            else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for authorizing lending
@app.callback(
    [
        Output('lendingconfirm_alert', 'color'),
        Output('lendingconfirm_alert', 'children'),
        Output('lendingconfirm_alert', 'is_open'),
    ],
    [
        Input('confirmlend_btn', 'n_clicks')
    ],
    [
        State('lend_password', 'value'),
        State('borrower_id', 'data'),
        State('lend_id', 'data'),
        State('return_duration', 'value'),
        State('currentuserid', 'data')
    ]
)

def authorize_lending(btn, password, user_id, accession_num, return_date, authorizing_id):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'confirmlend_btn' and btn:
            color = 'success'
            text = 'Resource successfully lent.'
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
                    sql = """SELECT borrow_id AS id FROM cartblock.borrowcart ORDER BY borrow_id DESC LIMIT 1;"""
                    values = []
                    cols = ['id']
                    df = db.querydatafromdatabase(sql, values, cols)
                    index = 1
                    if df.shape[0] > 0: index = df['id'][0] + 1
                    borrow_time = datetime.now(pytz.timezone('Asia/Manila'))
                    return_time = datetime.now(pytz.timezone('Asia/Manila')) + timedelta(days = return_date)
                    for i in accession_num:
                        sql = """INSERT INTO cartblock.borrowcart (borrow_id, user_id, accession_num, borrow_date, return_date, authorizing_id)
                                VALUES (%s, %s, %s, %s, %s, %s);
                                
                                UPDATE resourceblock.resourcecopy
                                SET circstatus_id = 2
                                WHERE accession_num = %s;"""
                        values = [index, user_id, int(i), borrow_time, return_time, authorizing_id, int(i)]
                        #print(values)
                        db.modifydatabase(sql, values)
                    sql = """UPDATE userblock.registereduser
                            SET borrowstatus_id = 2, borrowstatus_date = %s
                            WHERE user_id = %s;"""
                    values = [datetime.now(pytz.timezone('Asia/Manila')), user_id]
                    db.modifydatabase(sql, values)
            return [
                #None, None, None
                color, text, is_open
            ]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for cancelling wishlists
@app.callback(
    [
        Output('lend_alert', 'color'),
        Output('lend_alert', 'children'),
        Output('lend_alert', 'is_open'),
    ],
    [
        Input('url', 'pathname'),
        Input({'type' : 'cancellend_btn', 'index' : ALL}, 'n_clicks'),
    ],
    prevent_initial_call = True
)

def cancel_wishlists(pathname, btn):
    if pathname == '/circulation/wishlists':
        ctx = dash.callback_context
        if ctx.triggered[-1]['value'] == 0: raise PreventUpdate
        else:
            #print(ctx.triggered[0]['prop_id'].split('.')[0].split(',')[0].split(':')[1])
            eventid = ctx.triggered[0]['prop_id'].split('.')[0].split(',')[1].split(':')[1][1:-2]
            if eventid == 'cancellend_btn' and btn:
                color = 'success'
                text = 'Resource removed from wishlist.'
                is_open = True
                wishlist_id = ctx.triggered_id['index']
                sql = """UPDATE cartblock.wishlist
                    SET revert_time = %s
                    WHERE wishlist_id = %s;"""
                values = [datetime.now(pytz.timezone('Asia/Manila')), wishlist_id]
                db.modifydatabase(sql, values)
                return [color, text, is_open]
            else: raise PreventUpdate
    else: raise PreventUpdate

layout = html.Div(
    [
        dcc.Store(id = 'lend_id', storage_type = 'memory'),
        dcc.Store(id = 'borrower_id', storage_type = 'memory'),
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.H1("Active wishlists"),
                        html.Hr(),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'lend_alert',
                                    dismissable = True,
                                    duration = 5000,
                                    is_open = False
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    id = 'active_wishlists'
                                )
                            )
                        )
                    ]
                )
            ]
        ),
        dbc.Modal(
            [
                dbc.ModalHeader(dbc.ModalTitle("Confirm lending")),
                dbc.ModalBody(
                    [
                        dbc.Row(
                            dbc.Col(
                                html.P(id = 'borrower_name'),
                                width = 'auto'
                            ), justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Card(
                                    dbc.CardBody(
                                        id = 'lend_information'
                                    ), className = 'p-3 m-3'
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                "To lend these resources, please set the return window below:",
                                width = 'auto'
                                #lg = {'size' : '6', 'offset' : '3'}
                            ),
                            className = 'mb-3',
                            justify = 'center'
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Input(
                                            type = 'number',
                                            value = 1,
                                            min = 1,
                                            id = 'return_duration'
                                        ),
                                        dbc.FormText("Days")
                                    ],
                                    lg = 2
                                ),
                                dbc.Col(
                                    [
                                        html.Small("The window for returning resources is set to one (1) day by default.")
                                    ],
                                    lg = 3
                                )
                            ],
                            className = 'mb-3',
                            justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                "Finally, please enter your password to authorize the lending of these resources:",
                                lg = 6
                                #lg = {'size' : '6', 'offset' : '3'}
                            ),
                            className = 'mb-3',
                            justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'lendingconfirm_alert',
                                    dismissable = True,
                                    is_open = False
                                ),
                                #lg = {'size' : '6', 'offset' : '3'}
                                width = 6
                            ),
                            justify = 'center'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Input(
                                    type = 'password',
                                    id = 'lend_password',
                                    placeholder = 'Password'
                                ),
                                lg = 6
                            ),
                            className = 'mb-3',
                            justify = 'center'
                        )
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Confirm", id = 'confirmlend_btn')
                )
            ],
            id = 'lendingconfirm_modal',
            size = 'lg',
            is_open = False,
            centered = True,
            scrollable = True,
            backdrop = 'static'
        )
    ]
)