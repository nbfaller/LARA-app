from dash import dcc, html
import dash_bootstrap_components as dbc
from dash import dash_table
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import pandas as pd
import os
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
register_adapter(np.int64, AsIs)

from apps import commonmodules as cm
from app import app
from apps import dbconnect as db

@app.callback(
    [
        Output('rsearch_type', 'options'),
        Output('resourcetype_filter', 'options'),
        Output('subj_tier1_filter', 'options'),
        Output('library_filter', 'options'),
        Output('language_filter', 'options')
    ],
    [
        Input('url', 'pathname')
    ]
)

def populate_rdropdowns (pathname):
    if pathname == '/search' or pathname == '/resource/search':
        sql = """SELECT searchtype_desc AS label, searchtype_id AS value FROM utilities.searchtype;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        options1 = df.to_dict('records')

        sql = """SELECT resourcetype_name AS label, resourcetype_id AS value FROM utilities.resourcetype;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        options2 = df.to_dict('records')

        sql = """SELECT subj_tier1_name AS label, subj_tier1_id AS value FROM utilities.subjecttier1;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        options3 = df.to_dict('records')

        sql = """SELECT library_name AS label, library_id AS value FROM utilities.libraries;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        options4 = df.to_dict('records')

        sql = """SELECT language_name AS label, language_id AS value FROM utilities.languages;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        options5 = df.to_dict('records')

        return [options1, options2, options3, options4, options5]
    else: raise PreventUpdate

@app.callback(
    [
        Output('rsearch_results', 'children')
    ],
    [
        Input('url', 'pathname'),
        Input('rsearch_input', 'value'),
        Input('rsearch_type', 'value'),
        Input('resourcetype_filter', 'value'),
        Input('subj_tier1_filter', 'value'),
        Input('language_filter', 'value')
    ]
)

def generate_resourceresults (pathname, input, search_type, type, subj, lang):
    if pathname == '/search' or pathname == '/resource/search':
        sql = """SELECT r.title_id AS id, r.resource_title AS title, EXTRACT(YEAR FROM r.copyright_date) AS date,
        r_t.resourcetype_name AS type, r_s1.subj_tier1_name AS subj
        FROM resourceblock.resourcetitles AS r
        LEFT JOIN utilities.resourcetype AS r_t ON r.resourcetype_id = r_t.resourcetype_id
        LEFT JOIN utilities.subjecttier1 AS r_s1 ON r.subj_tier1_id = r_s1.subj_tier1_id
        LEFT JOIN resourceblock.resourceset AS r_s ON r.title_id = r_s.title_id
        LEFT JOIN resourceblock.resourceauthors AS r_a ON r.title_id = r_a.title_id
        LEFT JOIN resourceblock.authors AS a ON r_a.author_id = a.author_id
        """
        values = []
        cols = ['id', 'title', 'date', 'type', 'subj']

        sql_search = """SELECT searchtype_query AS query FROM utilities.searchtype WHERE searchtype_id = %s;"""
        values_search = [search_type]
        cols_search = ['query']
        df_search = db.querydatafromdatabase(sql_search, values_search, cols_search)

        if input:
            sql += df_search['query'][0]
            for i in range(len(df_search['query'][0].split("WHERE (")[1].split(")")[0].split(" OR "))):
                values += [f"%{input}%"]

        if type:
            sql += "AND ("
            c = 0
            for i in type:
                sql += "r.resourcetype_id = %s"
                values += [i]
                c += 1
                if c < len(type): sql += " OR "
            sql += ")"
        
        if subj:
            sql += "AND ("
            c = 0
            for i in subj:
                sql += "r.subj_tier1_id = %s"
                values += [i]
                c += 1
                if c < len(subj): sql += " OR "
            sql += ")"
        
        if lang:
            sql += "AND ("
            c = 0
            for i in lang:
                sql += "r.language_id = %s"
                values += [i]
                c += 1
                if c < len(lang): sql += " OR "
            sql += ")"
        
        sql += """ORDER BY r.title_id;"""
        df = db.querydatafromdatabase(sql, values, cols)
        results = []
        for i in df.index:
            authors = ''
            sql = """SELECT a.author_lname AS lname, a.author_fname AS fname
                FROM resourceblock.resourceauthors as r_a
                INNER JOIN resourceblock.authors AS a ON r_a.author_id = a.author_id
                WHERE r_a.title_id = %s;"""
            values = [df['id'][i]]
            cols = ['lname', 'fname']
            df_util = db.querydatafromdatabase(sql, values, cols)
            for j in df_util.index:
                authors += '%s, %s' % (df_util['lname'][j], df_util['fname'][j])
                if j != len(df_util.index)-1:
                    authors += '; '
            results.append(
                dbc.Card(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    dbc.Checkbox(
                                        label = i+1,
                                        id = 'rsearch_result%s' % str(i+1)
                                    ),
                                    className = 'p-3'
                                ),
                                dbc.Col(
                                    dbc.CardBody(
                                        [
                                            dbc.Badge(
                                                df['type'][i],
                                                className = 'mb-1',
                                                color = 'primary'
                                            ), html.Br(),
                                            html.A(
                                                html.H4(df['title'][i]),
                                                href = '/resource/record?id=%s' % df['id'][i],
                                                #className = 'mb-0'
                                            ),
                                            html.Small("by %s" % authors), html.Br(),
                                            html.Small(
                                                ["Published %s" % df['date'][i]],
                                                className = 'card-text text-muted'
                                            )
                                        ]
                                    ),
                                    sm = 8,
                                    md = 10,
                                    #className = 'col-md-10'
                                )
                            ],
                            className = 'g-0 d-flex align-items-center'
                        )
                    ],
                    className = 'mb-3',
                    style = {'border-radius' : '15px'}
                )
            )
        return [results]
    else: raise PreventUpdate

layout = html.Div(
    [
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H6("Filters"), html.Hr(),
                        dbc.Row(
                            dbc.Accordion(
                                [
                                    dbc.AccordionItem(
                                        dbc.Checklist(id = 'resourcetype_filter'),
                                        title = "Resource type"
                                    ),
                                ]
                            ),
                            className = 'mb-3'
                        ),
                        dbc.Row(
                            dbc.Accordion(
                                [
                                    dbc.AccordionItem(
                                        dbc.Checklist(id = 'subj_tier1_filter'),
                                        title = "Subject"
                                    ),
                                ], start_collapsed = True
                            ),
                            className = 'mb-3'
                        ),
                        dbc.Row(
                            dbc.Accordion(
                                [
                                    dbc.AccordionItem(
                                        dbc.Checklist(id = 'library_filter'),
                                        title = "Library"
                                    ),
                                ], start_collapsed = True
                            ),
                            className = 'mb-3'
                        ),
                        dbc.Row(
                            dbc.Accordion(
                                [
                                    dbc.AccordionItem(
                                        dbc.Checklist(id = 'language_filter'),
                                        title = "Language"
                                    ),
                                ], start_collapsed = True
                            ),
                            className = 'mb-3'
                        ),
                    ],
                    lg = 2,
                    sm = 12,
                    style = {
                        'margin-right' : '2em',
                        'padding' : '1.5em'
                    }
                ),
                dbc.Col(
                    [
                        html.H1("Search Resources"),
                        dbc.Form(
                            [
                                dbc.Row(
                                    [
                                        dbc.Col(
                                            dbc.Input(
                                                id = 'rsearch_input',
                                                type = 'text',
                                                placeholder = "Search here"
                                            ),
                                            md = 6,
                                            sm = 12,
                                            className = 'mb-3'
                                        ),
                                        dbc.Col(
                                            dcc.Dropdown(
                                                id = 'rsearch_type',
                                                value = 1,
                                                clearable = False,
                                                placeholder = "Search by"
                                            ),
                                            md = 3,
                                            sm = 8,
                                            className = 'mb-3'
                                        ),
                                        dbc.Col(
                                            dbc.Button(
                                                "🔎 Search",
                                                id = 'rsearch_submit',
                                                n_clicks = 0,
                                                style = {'width' : '100%'}
                                            ),
                                            md = 3,
                                            sm = 4,
                                            className = 'mb-3'
                                        )
                                    ]
                                )
                            ]
                        ),
                        html.Hr(),
                        html.Div(id = 'rsearch_results')
                    ],
                    #width = 10
                )
            ]
        )
    ]
)