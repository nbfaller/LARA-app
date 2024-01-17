from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State, ALL
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
        State('url', 'search'),
        State('currentuserid', 'data')
    ]
)

def retrieve_record(pathname, search, user_id):
    if pathname == '/resource/record':
        title = 'Resource record'
        type = None
        table = None
        authors = ['by ']
        parsed = urlparse(search)
        library_holdings = []
        if parsed.query:
            record_id = parse_qs(parsed.query)['id'][0]

            # Title information table
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
            df.insert(0, "Information", [html.B('Call number'), html.B('Language'), html.B('Publisher'), html.B('Copyright date'), html.B('Edition'), html.B('Collection')], True)
            df = df.rename(columns={'Information' : '', 0 : ''})
            table = dbc.Table.from_dataframe(
                df, hover = True, size = 'sm', #style = {'width' : 'auto'}
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
            
            # Holdings information generation
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
            for name, group in df:
                if user_id != -1: buttons = []
                group = group[['Accession #', 'Call #', 'Vol. #', 'Series #', 'Circ. type', 'Status']]
                for j in group['Status'].index:
                    badge_color = 'secondary'
                    if group['Status'][j] == 'On-shelf':
                        badge_color = 'primary'
                        if user_id != -1: 
                            buttons.append(
                                html.Div(
                                    dbc.Button(
                                        "Borrow",
                                        #href = 'record?id=%s&borrow=%s' % (record_id, group['Accession #'][j]),
                                        color = 'primary',
                                        size = 'sm',
                                        id = {'type' : 'borrow_btn', 'index' : j},
                                        n_clicks = 0
                                    ),
                                    #style = {'text-align' : 'center'}
                                )
                            )
                    else:
                        if user_id != -1: 
                            buttons.append(
                                html.Div(
                                    dbc.Button(
                                        "Borrow",
                                        color = 'secondary',
                                        size = 'sm',
                                        id = {'type' : 'borrow_btn', 'index' : j},
                                        disabled = True,
                                        outline = True
                                    ),
                                    #style = {'text-align' : 'center'}
                                )
                            )
                    #print(buttons)
                    group.loc[j, 'Status'] = dbc.Badge(group['Status'][j], color = badge_color)
                if user_id != -1: group['Action'] = buttons
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

# Callback for confirming resource reservation
@app.callback(
    [
        Output('reserve_modal', 'is_open'),
        Output('reserve_modalbody', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input({'type' : 'borrow_btn', 'index' : ALL}, 'n_clicks'),
    ],
    [
        State('url', 'search')
    ],
    prevent_initial_call = True
)

def confirm_rreservation(pathname, btn, search):
    if pathname == '/resource/record':
        ctx = dash.callback_context
        is_open = False
        body = []
        if ctx.triggered[-1]['value'] == None: raise PreventUpdate
        else:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0].split(',')[1].split(':')[1][1:-2]
            if eventid == 'borrow_btn' and btn:
                parsed = urlparse(search)
                record_id = None
                reserve_id = ctx.triggered_id['index']
                if parsed.query:
                    if parse_qs(parsed.query).get('id'):
                        record_id = parse_qs(parsed.query)['id'][0]
                        is_open = True
                        sql = """SELECT r.resource_title AS title, r.call_num AS callnum, r.resource_edition AS ed,
                            r_t.resourcetype_name AS type, r_l.language_name AS lang, r_c.collection_id AS coll, r_p.publisher_name AS pub,
                            r.copyright_date AS date
                            FROM resourceblock.resourcetitles AS r
                            LEFT JOIN utilities.resourcetype AS r_t ON r.resourcetype_id = r_t.resourcetype_id
                            LEFT JOIN utilities.languages AS r_l ON r.language_id = r_l.language_id
                            LEFT JOIN resourceblock.collections AS r_c ON r.collection_id  = r_c.collection_id
                            LEFT JOIN resourceblock.publishers AS r_p ON r.publisher_id = r_p.publisher_id
                            WHERE r.title_id = %s;
                        """
                        values = [record_id]
                        cols = ['Title', 'Call number', 'Edition', 'Type', 'Language', 'Collection', 'Publisher', 'Copyright date']
                        df = db.querydatafromdatabase(sql, values, cols)
                        #print(df)
                        body += [
                            dbc.Badge(df['Type'], color = 'primary'),
                            html.H4(df['Title']),
                        ]
                return [is_open, body]
            else: raise PreventUpdate
    else: raise PreventUpdate

layout = [
    dbc.Row(
        [
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
                                    className = 'mb-3 col-sm-12 col-lg-10'
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
                                ), width = 12
                            ),
                            id = 'tabs_profile'
                        )
                    ]
                ), lg = {'size' : 10, 'offset' : 1}
            )
        ]
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(html.H4('Confirm reservation')),
            dbc.ModalBody(
                [
                    html.P("You are seeking to borrow the following resource: "), html.Br(),
                    html.Div(id = 'reserve_modalbody'), html.Br(),
                    html.P(["To confirm your reservation, please click the ", html.B("Confirm"), " button below."]),
                    html.Hr(),
                    html.Small(
                        [
                            "Please note that upon reservation, the resource will be ",
                            html.B("blocked"),
                            " from lending ",
                            html.B("for one hour"),
                            ". You are advised to proceed to the library before then. Reservations that remain unborrowed by then will be forfeited and its circulation status will be reverted to on-shelf.",
                        ]
                    )
                ]
            ),
            dbc.ModalFooter(
                [
                    dbc.Button(
                        "Confirm",
                        id = 'confirm_btn',
                    ),
                ]
            )
        ],
        centered = True,
        scrollable = True,
        id = 'reserve_modal',
        backdrop = 'static'
    )
]