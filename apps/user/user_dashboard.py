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

# Callback for generating borrowing history table
@app.callback(
    [
        Output('active_borrows', 'children'),
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
        sql = """SELECT c.accession_num AS accession_num, r_t.resource_title AS title,
            TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bdate,
            TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS rdate,
            c_s.resourcestatus_name AS status, c.overdue_fine AS ofine, c.overdue_mins AS omins
            FROM cartblock.borrowcart AS c
            LEFT JOIN utilities.resourcestatus AS c_s ON c.resourcestatus_id = c_s.resourcestatus_id
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            WHERE c.user_id = %s AND c.resourcestatus_id <> 2;
        """
        values = [user_id]
        cols = ['Accession #', 'Title', 'Borrow date', 'Return date', 'Status', 'Overdue fine', 'Overdue minutes']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0] > 0: table1 = dbc.Table.from_dataframe(df, hover = True, size = 'sm')

        sql = """SELECT c.accession_num AS accession_num, r_t.resource_title AS title,
            TO_CHAR(c.borrow_date, 'Month dd, yyyy • HH:MI:SS AM') AS bdate,
            TO_CHAR(c.return_date, 'Month dd, yyyy • HH:MI:SS AM') AS rdate,
            c_s.resourcestatus_name AS status, c.overdue_fine AS ofine, c.overdue_mins AS omins
            FROM cartblock.borrowcart AS c
            LEFT JOIN utilities.resourcestatus AS c_s ON c.resourcestatus_id = c_s.resourcestatus_id
            LEFT JOIN resourceblock.resourcecopy AS r_c ON c.accession_num = r_c.accession_num
            LEFT JOIN resourceblock.resourceset AS r_s ON r_s.resource_id = r_c.resource_id
            LEFT JOIN resourceblock.resourcetitles AS r_t ON r_t.title_id = r_s.title_id
            WHERE c.user_id = %s AND c.resourcestatus_id = 2;
        """
        values = [user_id]
        cols = ['Accession #', 'Title', 'Borrow date', 'Return date', 'Status', 'Overdue fine', 'Overdue minutes']
        df = db.querydatafromdatabase(sql, values, cols)
        if df.shape[0] > 0: table3 = dbc.Table.from_dataframe(df, hover = True, size = 'sm')

        return [table1, table3]
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
                        html.Div(
                            [
                                html.H4("Borrowed resources"),
                                dbc.Card(
                                    dbc.CardBody(
                                        "You have no borrowed resources at the moment",
                                        id = 'active_borrows',
                                        className = 'p-3'
                                    )
                                )
                            ], className = 'mb-3'
                        ),
                        html.Div(
                            [
                                html.H4("Active reservations"),
                                dbc.Card(
                                    dbc.CardBody(
                                        "You have no active reservations at the moment",
                                        id = 'active_reserves',
                                        className = 'p-3'
                                    )
                                )
                            ], className = 'mb-3'
                        ),
                        html.Div(
                            [
                                html.H4("Borrowing history"),
                                dbc.Card(
                                    dbc.CardBody(
                                        id = 'borrowing_history',
                                        className = 'p-3'
                                    )
                                )
                            ], className = 'mb-3'
                        ),
                    ]
                )
            ]
        )
    ]
)