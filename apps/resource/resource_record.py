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

# Callback for setting record values
@app.callback(
    [
        Output('record_type', 'children'),
        Output('record_title', 'children'),
        Output('record_authors', 'children'),
        Output('record_table', 'children'),
        Output('holdings_profile', 'children')
    ],
    [
        Input('url', 'pathname')
    ],
    [
        State('url', 'search')
    ]
)

def retrieve_record(pathname, search):
    if pathname == '/resource/record':
        title = 'Resource record'
        type = None
        table = None
        authors = ['by ']
        parsed = urlparse(search)
        if parsed.query:
            record_id = parse_qs(parsed.query)['id'][0]
            sql = """SELECT r.call_num, r.resource_title, r.resource_edition,
                r_t.resourcetype_name, r_l.language_name, r_c.collection_name, r_p.publisher_name,
                r.copyright_date
                FROM resourceblock.resourcetitles AS r
                LEFT JOIN utilities.resourcetype AS r_t ON r.resourcetype_id = r_t.resourcetype_id
                LEFT JOIN utilities.languages AS r_l ON r.language_id = r_l.language_id
                LEFT JOIN resourceblock.collections AS r_c ON r.collection_id = r_c.collection_id
                LEFT JOIN resourceblock.publishers AS r_p ON r.publisher_id = r_p.publisher_id
                WHERE r.title_id = %s;"""
            values = [record_id]
            cols = ['Call number', 'Title', 'Edition', 'Resource type', 'Language', 'Collection', 'Publisher', 'Copyright date']
            df = db.querydatafromdatabase(sql, values, cols)
            title = df['Title'][0]
            type = df['Resource type'][0]
            df = df[['Call number', 'Language', 'Publisher', 'Copyright date', 'Edition', 'Collection']].transpose()
            df.insert(0, "Information", ['Call number', 'Language', 'Publisher', 'Copyright date', 'Edition', 'Collection'], True)
            table = dbc.Table.from_dataframe(
                df, hover = True, size = 'sm',
            )

            sql = """SELECT a.author_id AS id, a.author_lname AS lname, a.author_fname AS fname, a.author_mname AS mname
                FROM resourceblock.resourceauthors AS r_a
                LEFT JOIN resourceblock.authors AS a ON r_a.author_id = a.author_id
                WHERE r_a.title_id = %s;"""
            values = [record_id]
            cols = ['id', 'lname', 'fname', 'mname']
            df = db.querydatafromdatabase(sql, values, cols)
            lname = ''
            fname = ''
            mname = ''
            i = 0
            while i < df.shape[0]:
                if df['lname'][0]: lname = df['lname'][0]
                if df['fname'][0]: fname = df['fname'][0]
                if df['mname'][0]: mname = " " + df['mname'][0][0] + "."
                authors.append(
                    html.A(
                        "%s, %s%s" % (lname, fname, mname),
                        href = '/search?author_id=%s' % df['id'][0]
                    )
                )
                if i < df.shape[0] - 1: authors.append(";")
                i += 1
            
            sql = """SELECT c.accession_num AS accession,
                s.resource_volnum AS volnum,
                s.resource_seriesnum AS seriesnum,
                s.resource_desc AS desc,
                s.resource_contents AS contents,
                s.resource_isbn AS isbn,
                s.resource_issn AS issn,
                c.resource_copynum AS copynum,
                c_t.circtype_name AS circtype,
                c_s.circstatus_name AS circstatus,
                c_l.library_name AS library,
                copy_callnum AS callnum
                FROM resourceblock.resourceset AS s
                LEFT JOIN resourceblock.resourcecopy AS c ON s.resource_id = c.resource_id
                LEFT JOIN utilities.circulationtype AS c_t ON c.circtype_id = c_t.circtype_id
                LEFT JOIN utilities.circulationstatus AS c_s ON c.circstatus_id = c_s.circstatus_id
                LEFT JOIN utilities.libraries AS c_l ON c.library_id = c_l.library_id
                WHERE s.title_id = %s AND c_t.circtype_id <> 5;
                """
            values = [record_id]
            cols = ['Accession #', 'Vol. #', 'Series #', 'Description', 'Table of contents', 'ISBN', 'ISSN', 'Copy #', 'Circ. type', 'Status', 'Library', 'Call #']
            df = db.querydatafromdatabase(sql, values, cols)
            df = df[['Library', 'Accession #', 'Call #', 'Vol. #', 'Series #', 'Circ. type', 'Status']].groupby('Library')
            i = 0
            library_holdings = []
            for name, group in df:
                library_holdings.append(
                    dbc.Accordion(
                        dbc.AccordionItem(
                            dbc.Table.from_dataframe(group, hover = True, size = 'sm'),
                            title = name
                        ), className = 'mb-3'
                    )
                )
        return [type, title, authors, table, library_holdings]
    else: raise PreventUpdate

layout = [
    dbc.Row(
        [
            cm.sidebar,
            dbc.Col(
                html.Div(
                    [
                        dbc.Row(
                            dbc.Col(
                                dbc.Badge(
                                    "Resource type",
                                    id = 'record_type',
                                    color = 'success'
                                )
                            ), className = 'mb-1'
                        ),
                        dbc.Row(
                            [
                                html.H1(
                                    "Resource title",
                                    id = 'record_title'
                                )
                            ]
                        ),
                        dbc.Row(
                            [
                                html.P(
                                    "by authors",
                                    id = 'record_authors'
                                )
                            ], className = 'mb-3'
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        "Image here"
                                    ],
                                    className = 'mb-3 col-sm-4 col-lg-2'
                                ),
                                dbc.Col(
                                    id = 'record_table',
                                    className = 'mb-3 col-sm-11 col-lg-9'
                                )
                            ],
                            id = 'title_profile'
                        ),
                        dbc.Row(
                            dbc.Col(
                                dbc.Tabs(
                                    [
                                        dbc.Tab(
                                            html.Div(
                                                [
                                                    "Holdings information",
                                                ],
                                                id = 'holdings_profile',
                                                className = 'mt-3'
                                            ),
                                            label = 'Holdings'
                                        ),
                                        dbc.Tab(
                                            html.Div(
                                                [
                                                    "Description information"
                                                ],
                                                className = 'mt-3'
                                            ),
                                            label = 'Description',
                                            id = 'desc_profile'
                                        ),
                                        dbc.Tab(
                                            html.Div(
                                                [
                                                    "Table of contents"
                                                ],
                                                className = 'mt-3'
                                            ),
                                            label = 'Table of contents',
                                            id = 'contents_profile'
                                        )
                                    ],
                                ), width = 11
                            ),
                            id = 'tabs_profile'
                        )
                    ]
                )
            )
        ]
    )
]