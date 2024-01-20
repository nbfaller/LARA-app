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
            WHERE r_c.circstatus_id = 2;
        """
        values = []
        cols = ['id', 'Accession #', 'Title', 'Title ID', 'Library ID', 'Library', 'user_id', 'lname', 'fname', 'mname', 'livedname', 'Borrowed on', 'Return on', 'bordate', 'retdate']
        df = db.querydatafromdatabase(sql, values, cols)

        # Render user names
        lname = ''
        fname = ''
        mname = ''
        users = []
        # Action buttons
        buttons = []
        # Status badges
        statuses = []
        badge_color = 'secondary'
        badge_text = 'Borrowed'
        for i in df.index:
            df.loc[i, 'Title'] = html.A(df['Title'][i], href = '/resource/record?id=%s' % df['Title ID'][i])
            # Combine user names into single line
            lname = df['lname'][i]
            if df['livedname'][i] != None: fname = df['livedname'][i]
            else: fname = df['fname'][i]
            if df['mname'][i] != None: mname = " " + df['mname'][i][0] + "."
            else: mname = ''
            # Determine status
            remaining_time = (df['retdate'][i] - datetime.now(pytz.timezone('Asia/Manila'))).total_seconds()/(60*60)
            if remaining_time <= 1 and remaining_time >= 0:
                badge_color = 'warning'
            elif remaining_time < 0:
                badge_color = 'danger'
                badge_text = "Overdue"
            # Append user names, statuses, and buttons for returning
            users.append(html.A(["%s, %s%s" % (lname, fname, mname)], href = '/user/profile?mode=view&id=%s' %df['user_id'][i]))
            statuses.append(dbc.Badge(badge_text, color = badge_color))
            buttons.append(
                html.Div(
                    dbc.Button(
                        "Return",
                        color = 'primary',
                        size = 'sm',
                        id = {'type' : 'return_btn', 'index' : str(df['id'][i]) + "&" + str(df['user_id'][i])},
                        #href = '#',
                        n_clicks = 0
                    ),
                    #style = {'text-align' : 'center'}
                )
            )
        df.insert(2, "User", users, True)
        df.insert(5, "Status", statuses, True)
        df.insert(6, "Action", buttons, True)
        if df.shape[0] > 0:
            df = df.groupby('Library ID')
            for name, group in df:
                name = group['Library'].drop_duplicates().iloc[0]
                group = group[['Accession #', 'Title', 'User', 'Borrowed on', 'Return on', 'Status', 'Action']].sort_values(by = ['Borrowed on'])
                tables.append(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            dbc.Table.from_dataframe(group, hover = True, size = 'sm'),
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
        Output('return_id', 'data'),
        Output('returner_id', 'data'),
        Output('retcon_alert', 'children'),
        Output('retcon_alert', 'color'),
        Output('confirmreturn_text', 'children')
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
        if ctx.triggered[-1]['value'] == 0: raise PreventUpdate
        else:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0].split(',')[1].split(':')[1][1:-2]
            if eventid == 'return_btn' and btn:
                is_open = True
                content = []
                borrow_id = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1].split("&")[0][1:]
                user_id = ctx.triggered[-1]['prop_id'].split('.')[0].split(',')[0].split(':')[1].split("&")[1][:-1]
                confirmreturn_text = ["Please enter your password to confirm the return of this resource."]

                sql = """SELECT c.accession_num AS accession_num, u.user_lname AS lname, u.user_fname AS fname, u.user_mname AS mname, u.user_livedname AS livedname, u.borrowstatus_id AS status,
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
                    'Accession #', 'lname', 'fname', 'mname', 'livedname', 'status', 'bordate', 'retdate', 'raw_bordate', 'raw_retdate',
                    'Title', 'Title ID', 'Type', 'Call #', 'Language', 'Publisher', 'Copyright date', 'Edition',
                    'Collection', 'Library'
                ]
                df = db.querydatafromdatabase(sql, values, cols)
                title_id = df['Title ID'][0]
                resource_id = df['Accession #'][0]

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
                        ]
                    )
                )
                
                authors = ["by "]
                sql = """SELECT a.author_lname AS lname, a.author_fname AS fname, a.author_mname AS mname, a.author_id AS id
                    FROM resourceblock.resourceauthors AS r
                    LEFT JOIN resourceblock.authors AS a ON r.author_id = a.author_id
                    WHERE r.title_id = %s;"""
                values = [title_id]
                cols =['lname', 'fname', 'mname', 'id']
                df_authors = db.querydatafromdatabase(sql, values, cols)

                lname = ''
                fname = ''
                mname = ''
                for i in df_authors.index:
                    lname = df_authors['lname'][i]
                    if df_authors['fname'][i]: fname = df_authors['fname'][i]
                    if df_authors['mname'][i]: mname = " " + df_authors['mname'][i][0] + "."
                    authors.append(
                        html.A(
                            ["%s, %s%s" % (lname, fname, mname)],
                            href = '/search?author_id=%s' % df_authors['id'][i]
                        )
                    )
                    if i < df_authors.shape[0] - 2: authors.append(", ")
                    elif i == df_authors.shape[0] - 2: authors.append(", & ")

                card_content = [
                    dbc.Badge(df['Type'][0], color = 'success', className = 'mb-1'),
                    html.H4(df['Title'][0], className = 'mb-0'),
                    html.Span(authors)
                ]

                table = df[['Call #', 'Language', 'Publisher', 'Copyright date', 'Edition', 'Collection', 'Library']].transpose()
                table.insert(0, "Information", [html.B('Call number'), html.B('Language'), html.B('Publisher'), html.B('Copyright date'), html.B('Edition'), html.B('Collection'), html.B('Library')], True)
                table = table.rename(columns={'Information' : '', 0 : ''})
                card_content += [
                    dbc.Table.from_dataframe(
                        table, hover = True, size = 'sm'#, className = 'mb-3'
                    ),
                ]
                content.append(dbc.Card(dbc.CardBody(card_content), className = 'p-3 mb-3'))

                # Penalty determination
                sql = """SELECT penalty_value AS penalty, penalty_type AS type
                FROM utilities.penaltyperday
                ORDER BY penalty_id ASC ;"""
                values = []
                cols = ['penalty', 'type']
                df_penalty = db.querydatafromdatabase(sql, values, cols)

                retcon_text = "This resource will be returned on time."
                retcon_color = 'success'
                remaining_time = (df['raw_retdate'][0] - datetime.now(pytz.timezone('Asia/Manila'))).total_seconds()/(60*60)
                if remaining_time < 0:
                    penalty = math.ceil(abs(remaining_time/24))
                    retcon_text = [
                        "This resource is already ", html.B("OVERDUE"), ".",
                        " A payment of ", html.B("₱%s OR %s minutes of community service" % (df_penalty['penalty'][0]*penalty, df_penalty['penalty'][1]*penalty)),
                        " is required to clear this penalty."
                    ]
                    retcon_color = 'danger'
                    if df['status'][0] != 2:
                        sql = """UPDATE userblock.registereduser
                            SET borrowstatus_id = 2, borrowstatus_date = %s
                            WHERE user_id = %s;
                        """
                        values = [datetime.now(pytz.timezone('Asia/Manila')), user_id]
                        db.modifydatabase(sql, values)
                    confirmreturn_text += [
                            " ", html.B("Make sure that any penalties incurred have already been paid/rendered beforehand.")
                    ]
                return [is_open, content, resource_id, user_id, retcon_text, retcon_color, confirmreturn_text]
            else: raise PreventUpdate
    else: raise PreventUpdate

layout = html.Div(
    [
        dcc.Store(id = 'return_id', storage_type = 'memory'),
        dcc.Store(id = 'returner_id', storage_type = 'memory'),
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
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Span(id = 'confirmreturn_text'),
                            ),
                            className = 'mb-3'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Alert(
                                    id = 'confirmreturn_alert',
                                    dismissable = True,
                                    is_open = False
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Input(
                                    type = 'password',
                                    id = 'return_password',
                                    placeholder = 'Password'
                                ),
                                className = 'mb-3'
                            )
                        )
                    ]
                ),
                dbc.ModalFooter(
                    dbc.Button("Confirm", id = 'confirmreturn_btn')
                )
            ],
            id = 'confirmreturn_modal',
            scrollable = True
        )
    ]
)