from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
from datetime import datetime
import pytz

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

# Callback for generating borrowing history table
@app.callback(
    [
        Output('active_borrows', 'children'),
        Output('active_reserves', 'children'),
        Output('borrowing_history', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('currentuserid', 'data')
    ]
)

def generate_bhistory(pathname, user_id):
    if (pathname == '/user' or pathname == '/user/dashboard') and user_id != -1:
        table1 = "You have no borrowed resources at the moment"
        table2 = "You have no active reservations at the moment"
        table3 = "You are yet to borrow any resources. Visit the library today!"

        # Borrowed resources
        sql = """SELECT c.accession_num AS accession_num, r_t.resource_title AS title, r_t.title_id AS title_id,
            TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bdate, c.borrow_date AS raw_bdate,
            TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS rdate, c.return_date AS raw_rdate,
            c.overdue_fine AS ofine, c.overdue_mins AS omins
            FROM cartblock.borrowcart AS c
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            WHERE c.user_id = %s AND c.resourcestatus_id <> 2;
        """
        values = [user_id]
        cols = ['Accession #', 'Title', 'Title ID', 'Borrow date', 'raw_bdate', 'Return date', 'raw_rdate', 'Overdue fine', 'Overdue minutes']
        df = db.querydatafromdatabase(sql, values, cols)
        for i in df['Title'].index:
            df.loc[i, 'Title'] = html.A(df['Title'][i], href = '/resource/record?id=%s' % df['Title ID'][i])
        statuses = []
        badge_color = 'primary'
        badge_text = 'Borrowed'
        for i in df['raw_rdate']:
            remaining_time = (i - datetime.now(pytz.timezone('Asia/Manila'))).total_seconds()/(60*60)
            if remaining_time <= 1 and remaining_time >= 0:
                badge_color = 'warning'
            elif remaining_time < 0:
                badge_color = 'danger'
                badge_text = "Overdue"
            statuses.append(dbc.Badge(badge_text, color = badge_color))
        df.insert(8, "Status", statuses, True)
        df = df[['Accession #', 'Title', 'Borrow date', 'Return date', 'Status', 'Overdue fine', 'Overdue minutes']]
        if df.shape[0] > 0: table1 = dbc.Table.from_dataframe(df, hover = True, size = 'sm')

        # Wishlist
        sql = """SELECT c.accession_num AS accession_num, r_t.resource_title AS title, r_t.title_id AS title_id,
            TO_CHAR(c.reserve_time, 'Month dd, yyyy • HH:MI:SS AM') AS resdate,
            TO_CHAR(c.revert_time, 'Month dd, yyyy • HH:MI:SS AM') AS revdate
            FROM cartblock.wishlist AS c
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            WHERE c.user_id = %s AND c.revert_time >= CURRENT_TIMESTAMP AND r_c.circstatus_id <> 2;
        """
        values = [user_id]
        cols = ['Accession #', 'Title', 'Title ID', 'Added on', 'Expires by']
        df = db.querydatafromdatabase(sql, values, cols)
        for i in df['Title'].index:
            df.loc[i, 'Title'] = html.A(df['Title'][i], href = '/resource/record?id=%s' % df['Title ID'][i])
        df = df[['Accession #', 'Title', 'Added on', 'Expires by']]
        if df.shape[0] > 0: table2 = dbc.Table.from_dataframe(df, hover = True, size = 'sm')

        # Borrowing history
        sql = """SELECT c.accession_num AS accession_num, r_t.resource_title AS title,
            TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bdate,
            TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS rdate,
            c.overdue_fine AS ofine, c.overdue_mins AS omins
            FROM cartblock.borrowcart AS c
            LEFT JOIN utilities.resourcestatus AS c_s ON c.resourcestatus_id = c_s.resourcestatus_id
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            WHERE c.user_id = %s AND c.resourcestatus_id = 2 AND c.return_date < CURRENT_TIMESTAMP;
        """
        values = [user_id]
        cols = ['Accession #', 'Title', 'Borrow date', 'Return date', 'Overdue fine', 'Overdue minutes']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0] > 0: table3 = dbc.Table.from_dataframe(df, hover = True, size = 'sm')

        return [table1, table2, table3]
    else: raise PreventUpdate

layout = html.Div(
    [
        dbc.Row(
            [
                cm.sidebar,
                dbc.Col(
                    [
                        html.H1(['Dashboard']),
                        html.Hr(),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H4("📚 Borrowed resources"),
                                        dbc.Card(
                                            dbc.CardBody(
                                                "You have no borrowed resources at the moment",
                                                id = 'active_borrows',
                                                className = 'p-3'
                                            )
                                        )
                                    ], className = 'mb-3'
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H4("🌟 Wishlist"),
                                        dbc.Card(
                                            dbc.CardBody(
                                                "You have no active reservations at the moment",
                                                id = 'active_reserves',
                                                className = 'p-3'
                                            )
                                        )
                                    ], className = 'mb-3'
                                )
                            )
                        ),
                        dbc.Row(
                            dbc.Col(
                                html.Div(
                                    [
                                        html.H4("📜 Borrowing history"),
                                        dbc.Card(
                                            dbc.CardBody(
                                                id = 'borrowing_history',
                                                className = 'p-3'
                                            )
                                        )
                                    ], className = 'mb-3'
                                )
                            )
                        ),
                    ]
                )
            ]
        )
    ]
)