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
        Output('publisher_id', 'options'),
        Output('collection_id', 'options'),
        Output('library_id', 'options'),
        Output('existing_titles', 'options'),
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

        # Collections
        sql = """SELECT collection_name as label, collection_id as value
            FROM resourceblock.collections;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['label'])
        collections = df.to_dict('records')

        # Libraries
        sql = """SELECT library_name as label, library_id as value
            FROM utilities.libraries;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
        libraries = df.to_dict('records')

        # Existing titles
        sql = """SELECT CONCAT(t.resource_title, ' (', p.publisher_name, ', ', EXTRACT(YEAR FROM t.copyright_date), ')') as label, title_id as value
            FROM resourceblock.resourcetitles AS t
            LEFT JOIN resourceblock.publishers as p ON t.publisher_id = p.publisher_id;"""
        values = []
        cols = ['label', 'value']
        df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['label'])
        titles = df.to_dict('records')

        return [resourcetype, subjecttier1, authors, languages, publishers, collections, libraries, titles]
    else: raise PreventUpdate

# Callback for populating existing sets dropdown
@app.callback(
    [
        Output('existing_sets', 'options')
    ],
    [
        Input('url', 'pathname'),
        Input('existing_titles', 'value')
    ]
)

def populate_resourcesets(pathname, title):
    if pathname == '/resource/catalog':
        sets = []
        if title:
            sql = """SELECT CONCAT('Vol. #: ', resource_volnum, '; Series #: ', resource_seriesnum, '; ISBN/ISSN: ', resource_isbn, resource_issn) AS label,
                resource_id AS value
                FROM resourceblock.resourceset
                WHERE title_id = %s;"""
            values = [title]
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
            sets = df.to_dict('records')
        return [sets]
    else: raise PreventUpdate

# Callback for populating existing sets dropdown
@app.callback(
    [
        Output('resource_volnum', 'value'), Output('resource_volnum', 'disabled'),
        Output('resource_seriesnum', 'value'), Output('resource_seriesnum', 'disabled'),
        Output('resource_isbn', 'value'), Output('resource_isbn', 'disabled'),
        Output('resource_issn', 'value'), Output('resource_issn', 'disabled'),
        Output('resource_desc', 'value'), Output('resource_desc', 'disabled'),
        Output('resource_contents', 'value'), Output('resource_contents', 'disabled'),
    ],
    [
        Input('url', 'pathname'),
        Input('existing_titles', 'value'),
        Input('existing_sets', 'value')
    ]
)

def populate_resourcesets(pathname, title, set):
    if pathname == '/resource/catalog':
        volnum = None
        volnum_disabled = False
        seriesnum = None
        seriesnum_disabled = False
        isbn = None
        isbn_disabled = False
        issn = None
        issn_disabled = False
        desc = None
        desc_disabled = False
        contents = None
        contents_disabled = False
        if title and set:
            sql = """SELECT resource_volnum AS volnum, resource_seriesnum AS seriesnum, resource_isbn AS isbn, resource_issn AS issn,
                resource_desc AS desc, resource_contents AS contents
                FROM resourceblock.resourceset
                WHERE title_id = %s AND resource_id = %s;"""
            values = [title, set]
            cols = ['volnum', 'seriesnum', 'isbn', 'issn', 'desc', 'contents']
            df = db.querydatafromdatabase(sql, values, cols) 
            volnum = df['volnum']
            volnum_disabled = True
            seriesnum = df['seriesnum']
            seriesnum_disabled = True
            isbn = df['isbn']
            isbn_disabled = True
            issn = df['issn']
            issn_disabled = True
            desc = df['desc']
            desc_disabled = True
            contents = df['contents']
            contents_disabled = True
        return [
            volnum, volnum_disabled,
            seriesnum, seriesnum_disabled,
            isbn, isbn_disabled,
            issn, issn_disabled,
            desc, desc_disabled,
            contents, contents_disabled
        ]
    else: raise PreventUpdate

# Callback for disabling inputs and setting values if title is selected
@app.callback(
    [
        Output('resourcetype_id', 'value'), Output('resourcetype_id', 'disabled'),
        Output('resource_title', 'value'), Output('resource_title', 'disabled'),
        Output('author_lname', 'disabled'),
        Output('author_fname', 'disabled'),
        Output('author_mname', 'disabled'),
        Output('resource_authors', 'value'), Output('resource_authors', 'disabled'),
        Output('newauthor_btn', 'disabled'),
        Output('subj_tier1_id', 'value'), Output('subj_tier1_id', 'disabled'),
        Output('copyright_date', 'date'), Output('copyright_date', 'disabled'),
        Output('resource_edition', 'value'), Output('resource_edition', 'disabled'),
        Output('language_id', 'value'), Output('language_id', 'disabled'),
        Output('collection_id', 'value'), Output('collection_id', 'disabled'),
        Output('publisher_id', 'value'), Output('publisher_id', 'disabled'),
        Output('publisher_name', 'disabled'),
        Output('publisher_loc', 'disabled'),
        Output('newpublisher_btn', 'disabled'),
    ],
    [
        Input('url', 'pathname'),
        Input('existing_titles', 'value')
    ]
)

def set_existingtitle(pathname, title):
    if pathname == '/resource/catalog':
        if title:
            sql = """SELECT resourcetype_id as type, resource_title as title,
                subj_tier1_id as t1, copyright_date as date, resource_edition as ed,
                language_id as lang, collection_id as col, publisher_id as pub
                FROM resourceblock.resourcetitles
                WHERE title_id = %s;"""
            values = [title]
            cols = ['type', 'title', 't1', 'date', 'ed', 'lang', 'col', 'pub']
            df = db.querydatafromdatabase(sql, values, cols)

            sql = """SELECT author_id as author
                FROM resourceblock.resourceauthors
                WHERE title_id = %s;"""
            cols = ['author']
            df2 = db.querydatafromdatabase(sql, values, cols)
            authors = df2['author'].to_list()
            return [
                df['type'][0], True,
                df['title'][0], True,
                True,
                True,
                True,
                authors, True,
                True,
                df['t1'][0], True,
                df['date'][0], True,
                df['ed'][0], True,
                df['lang'][0], True,
                df['col'][0], True,
                df['pub'][0], True,
                True,
                True,
                True
            ]
        else: return [
            None, False,
            None, False,
            False,
            False,
            False,
            None, False,
            False,
            None, False,
            None, False,
            None, False,
            None, False,
            None, False,
            None, False,
            False,
            False,
            False
        ]
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
        Input('subj_tier1_id', 'value'),
        Input('existing_titles', 'value')
    ]
)

def populate_subjecttier2(pathname, t1, title):
    if pathname == '/resource/catalog':
        options = {}
        value = None
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
            if title:
                sql = """SELECT subj_tier2_id as value
                    FROM resourceblock.resourcetitles
                    WHERE title_id = %s;"""
                values = [title]
                cols = ['value']
                df = db.querydatafromdatabase(sql, values, cols)
                value = df['value'][0]
            else: disabled = False
        return [options, value, disabled]
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
        Input('subj_tier2_id', 'value'),
        Input('existing_titles', 'value')
    ]
)

def populate_subjecttier3(pathname, t1, t2, title):
    if pathname == '/resource/catalog':
        options = {}
        value = None
        disabled = True
        if t1 != None and t1 >= 0 and t2 != None and t2 >= 0:
            sql = """SELECT CONCAT(TO_CHAR(subj_tier1_id*100 + subj_tier2_id*10 + subj_tier3_id, '000'), ' ', subj_tier3_name) as label, subj_tier3_id as value
                FROM utilities.subjecttier3 WHERE subj_tier1_id = %s AND subj_tier2_id = %s AND subj_tier3_name IS NOT NULL;"""
            values = [t1, t2]
            cols = ['label', 'value']
            df = db.querydatafromdatabase(sql, values, cols).sort_values(by = ['value'])
            options = df.to_dict('records')
            if title:
                sql = """SELECT subj_tier3_id as value
                    FROM resourceblock.resourcetitles
                    WHERE title_id = %s;"""
                values = [title]
                cols = ['value']
                df = db.querydatafromdatabase(sql, values, cols)
                value = df['value'][0]
            else: disabled = False
        return [options, value, disabled]
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
        L1 = '•••'
        L2 = '••••'
        L3 = '••••'
        if t1 != None and t1 >= 0:
            L1 = str(t1*100).zfill(3)
            if t2 != None and t2 >= 0:
                L1 = str(t1*100 + t2*10).zfill(3)
                if t3 != None and t3 >= 0:
                    L1 = str(t1*100 + t2*10 + t3).zfill(3)
        if res_authors:
            cutternums = []
            for i in res_authors:
                sql = """SELECT author_cutternum as num FROM resourceblock.authors WHERE author_id = %s;"""
                values = [i]
                cols = ['num']
                df = db.querydatafromdatabase(sql, values, cols)
                cutternums.append(df['num'][0])
            cutternums.sort()
            L2 = cutternums[0]
        if date:
            L3 = date.split("-")[0]
        if L1 != '•••' or L2 != '••••' or L3 != '••••':
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
                if lname == '' or lname == None: lname = ''
                if fname == '' or fname == None: fname = ''
                if mname == '' or mname == None: mname = ''
                alert_text = ''
                alert_color = ''
                alert_open = True
                if lname and fname:
                    cs_num = None
                    sql = """SELECT author_id AS id
                        FROM resourceblock.authors
                        WHERE author_lname = %s AND author_fname = %s AND author_mname = %s;"""
                    values = [lname, fname, mname]
                    cols = ['id']
                    df = db.querydatafromdatabase(sql, values, cols)
                    if not df.empty:
                        alert_text = "This author is already registered. Please select them in the dropdown menu above."
                        alert_color = 'danger'
                    else:
                        # Cutter sanborn number generator
                        for c in range(2, len(lname)+1):
                            sql = """SELECT cs_num AS num FROM utilities.cuttersanborn WHERE cs_char = %s AND cs_name ILIKE %s;"""
                            values = [lname[0], f"%{lname[0:c]}%"]
                            cols = ['num']
                            df = db.querydatafromdatabase(sql, values, cols)
                            if df.shape[0] == 1:
                                cs_num = lname[0]+str(df['num'][0])
                                break
                            elif df.shape[0] > 1 and c == len(lname):
                                name = lname + ', '
                                for n in range(1, len(fname) + 1):
                                    name += fname[n-1]
                                    sql = """SELECT cs_num AS num FROM utilities.cuttersanborn WHERE cs_char = %s AND cs_name ILIKE %s;"""
                                    values = [lname[0], f"%{name}%"]
                                    cols = ['num']
                                    df = db.querydatafromdatabase(sql, values, cols)
                                    if df.shape[0] == 1 or (df.shape[0] > 1 and n == len(fname)):
                                        cs_num = lname[0]+str(df['num'][0])
                                        break
                        sql = """INSERT INTO resourceblock.authors(author_lname, author_fname, author_mname, author_cutternum)
                            VALUES(%s, %s, %s, %s);"""
                        values = [lname, fname, mname, cs_num]
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
        Output('newpublisher_alert', 'is_open'),
        Output('publisher_name', 'value'),
        Output('publisher_loc', 'value'),
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

def register_publisher(pathname, btn, name, loc):
    if pathname == '/resource/catalog':
        ctx = dash.callback_context
        if ctx.triggered:
            eventid = ctx.triggered[0]['prop_id'].split('.')[0]
            if eventid == 'newpublisher_btn' and btn:
                if name == '' or name == None: name = ''
                if loc == '' or loc == None: loc = ''
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
                    else:
                        sql = """INSERT INTO resourceblock.publishers(publisher_name, publisher_loc)
                            VALUES(%s, %s);"""
                        values = [name, loc]
                        db.modifydatabase(sql, values)
                        alert_text = "New publisher successfully registered. Please select them in the dropdown menu above."
                        alert_color = 'success'
                        name = None
                        loc = None
                elif name == None or name == '':
                    alert_text = "Please input the publisher's name."
                    alert_color = 'warning'
                return [alert_text, alert_color, alert_open, name, loc]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for limiting maximum copies per classification type
@app.callback(
    [
        Output('copies_type2', 'max'),
        Output('copies_type3', 'max'),
        Output('copies_type2', 'value'),
        Output('copies_type3', 'value'),
        Output('copies_type1', 'value'),
    ],
    [
        Input('url', 'pathname'),
        Input('copies_total', 'value'),
        Input('copies_type2', 'value'),
        Input('copies_type3', 'value'),
    ]
)

def set_maxpertype(pathname, copies, t2, t3):
    if pathname == '/resource/catalog':
        diff = copies - (t2 + t3)
        max2 = t2 + diff
        max3 = t3 + diff
        if diff < 0:
            if t2 > t3: t2 -= 1
            elif t3 > t2 or t2 == t3: t3 -= 1
        t1 = copies - (t2 + t3)
        return [max2, max3, t2, t3, t1]
    else: raise PreventUpdate

# Callback for confirming details
@app.callback(
    [
        Output('catalog_alert', 'color'),
        Output('catalog_alert', 'children'),
        Output('catalog_alert', 'is_open'),
        Output('catalog_modalbody', 'children'),
        Output('catalog_confirmationmodal', 'is_open')
    ],
    [
        Input('catalog_btn', 'n_clicks')
    ],
    [
        # Required values in resourceblock.resourcetitles
        State('call_num', 'value'),
        State('resource_title', 'value'),
        State('resource_edition', 'value'),
        State('resourcetype_id', 'value'),
        State('language_id', 'value'),
        State('collection_id', 'value'),
        State('publisher_id', 'value'),
        State('copyright_date', 'date'),
        State('subj_tier1_id', 'value'),
        State('subj_tier2_id', 'value'),
        State('subj_tier3_id', 'value'),
        # Required values in resourceblock.resourceset
        State('resource_volnum', 'value'),
        State('resource_seriesnum', 'value'),
        State('resource_isbn', 'value'),
        State('resource_issn', 'value'),
        State('resource_desc', 'value'),
        State('resource_contents', 'value'),
        # Required values in resourceblock.resourcecopy
        State('copies_total', 'value'),
        State('copies_type1', 'value'),
        State('copies_type2', 'value'),
        State('copies_type3', 'value'),
        State('library_id', 'value'),
        # Required values in resourceblock.resourceauthors
        State('resource_authors', 'value'),
    ]
)

def confirmation(btn, callnum, title, ed, type, lang, collect,
                 pub, date, subjt1, subjt2, subjt3, vol, series,
                 isbn, issn, desc, contents, copies, copiest1,
                 copiest2, copiest3, library, authors):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'catalog_btn' and btn:
            alert_color = ''
            alert_text = ''
            alert_open = False
            modal_content = ''
            modal_open = False

            if (callnum == None or title == None or type == None or
                subjt1 == None or subjt2 == None or subjt3 == None or
                copies == None or copiest1 == None or copiest2 == None or
                copiest3 == None or authors == None):
                alert_color = 'warning'
                alert_open = True
                alert_text = 'Insufficient information. Please fill out all required fields.'
            else:
                modal_open = True

                sql = """SELECT r_t.resourcetype_name AS type
                FROM utilities.resourcetype AS r_t
                WHERE r_t.resourcetype_id = %s;"""
                values = [type]
                cols = ['type']
                df = db.querydatafromdatabase(sql, values, cols)
                type = df['type'][0]

                sql = """SELECT CONCAT(TO_CHAR(subj_tier1_id*100 + subj_tier2_id*10 + subj_tier3_id, '000'), ' ', subj_tier3_name) AS subj
                FROM utilities.subjecttier3 AS t3
                WHERE t3.subj_tier1_id = %s AND t3.subj_tier2_id = %s AND t3.subj_tier3_id = %s;"""
                values = [subjt1, subjt2, subjt3]
                cols = ['subj']
                df = db.querydatafromdatabase(sql, values, cols)
                subj = df['subj'][0]

                authors_list = ''
                for i in authors:
                    sql = """SELECT author_lname AS lname, author_fname AS fname, author_mname AS mname
                    FROM resourceblock.authors
                    WHERE author_id = %s;"""
                    values = [i]
                    cols = ['lname', 'fname', 'mname']
                    df = db.querydatafromdatabase(sql, values, cols)
                    authors_list += df['lname'][0] + ", " + df['fname'][0]
                    if df['mname'][0] == None or df['mname'][0] == '': authors_list += "; "
                    else: authors_list += " " + df['mname'][0] + "; "
                authors_list = authors_list[:len(authors_list) - 2]

                sql = """SELECT library_name AS library
                FROM utilities.libraries
                WHERE library_id = %s;"""
                values = [library]
                cols = ['library']
                df = db.querydatafromdatabase(sql, values, cols)
                library = df['library'][0]

                title_optional = []
                set_information = []

                modal_content = [
                    html.H5("🗃️ Title information"),
                    html.B("Title: "), title, html.Br(),
                    html.B("Authors: "), authors_list, html.Br(),
                    html.B("Resource type: "), type, html.Br(),
                    html.B("Call number: "), callnum, html.Br(),
                    html.B("Subject classification: "), subj, html.Br(),
                    html.Div(title_optional), html.Br(),
                    html.Div(set_information),
                    html.H5("📗 Copy information"),
                    html.B("Library: "), library, html.Br(),
                    html.B("Total number of copies: "), copies, html.Br(),
                    "%s for regular circulation, %s for room-use only, and %s as reserves."% (copiest1, copiest2, copiest3)
                ]

                # Optional title information
                if ed:
                    title_optional.append(html.B("Edition: "))
                    title_optional.append(ed)
                    title_optional.append(html.Br())
                if lang:
                    sql = """SELECT language_name AS lang
                    FROM utilities.languages
                    WHERE language_id = %s;"""
                    values = [lang]
                    cols = ['lang']
                    df = db.querydatafromdatabase(sql, values, cols)
                    lang = df['lang'][0]
                    title_optional.append(html.B("Language: "))
                    title_optional.append(lang)
                    title_optional.append(html.Br())
                if collect:
                    sql = """SELECT collection_name AS collect
                    FROM resourceblock.collections
                    WHERE collection_id = %s;"""
                    values = [collect]
                    cols = ['collect']
                    df = db.querydatafromdatabase(sql, values, cols)
                    collect = df['collect'][0]
                    title_optional.append(html.B("Collection: "))
                    title_optional.append(collect)
                    title_optional.append(html.Br())
                if pub:
                    sql = """SELECT CONCAT(publisher_name, ' (', publisher_loc, ')') AS pub
                    FROM resourceblock.publishers
                    WHERE publisher_id = %s;"""
                    values = [pub]
                    cols = ['pub']
                    df = db.querydatafromdatabase(sql, values, cols)
                    pub = df['pub'][0]
                    title_optional.append(html.B("Publisher: "))
                    title_optional.append(pub)
                    title_optional.append(html.Br())
                if date:
                    title_optional.append(html.B("Copyright date: "))
                    title_optional.append(date)
                    title_optional.append(html.Br())
                if vol or series or isbn or issn or desc or contents:
                    set_information.append(html.H5("📚 Set information"),)
                    if vol:
                        set_information.append(html.B("Volume number: "))
                        set_information.append(vol)
                        set_information.append(html.Br())
                    if series:
                        set_information.append(html.B("Series number: "))
                        set_information.append(series)
                        set_information.append(html.Br())
                    if isbn:
                        set_information.append(html.B("ISBN: "))
                        set_information.append(isbn)
                        set_information.append(html.Br())
                    if issn:
                        set_information.append(html.B("ISSN: "))
                        set_information.append(issn)
                        set_information.append(html.Br())
                    if desc:
                        set_information.append(html.B("Description: "))
                        set_information.append(html.Br())
                        set_information.append(desc)
                        set_information.append(html.Br())
                    if contents:
                        set_information.append(html.B("Table of contents: "))
                        set_information.append(html.Br())
                        set_information.append(contents)
                        set_information.append(html.Br())
                    set_information.append(html.Br())
            return [alert_color, alert_text, alert_open, modal_content, modal_open]
        else: raise PreventUpdate
    else: raise PreventUpdate

# Callback for cataloging new resource
@app.callback(
    [
        Output('catalogconfirm_alert', 'color'),
        Output('catalogconfirm_alert', 'children'),
        Output('catalogconfirm_alert', 'is_open'),
    ],
    [
        Input('confirmcatalog_btn', 'n_clicks')
    ],
    [
        # User ID
        State('currentuserid', 'data'),
        # Password
        State('catalog_password', 'value'),
        # Required values in resourceblock.resourcetitles
        State('existing_titles', 'value'),
        State('resource_title', 'value'),
        State('call_num', 'value'),
        State('resourcetype_id', 'value'),
        State('resource_authors', 'value'),
        State('subj_tier1_id', 'value'),
        State('subj_tier2_id', 'value'),
        State('subj_tier3_id', 'value'),
        State('copyright_date', 'date'),
        State('resource_edition', 'value'),
        State('language_id', 'value'),
        State('collection_id', 'value'),
        State('publisher_id', 'value'),
        # Required values in resourceblock.resourceset
        State('existing_sets', 'value'),
        State('resource_volnum', 'value'),
        State('resource_seriesnum', 'value'),
        State('resource_isbn', 'value'),
        State('resource_issn', 'value'),
        State('resource_desc', 'value'),
        State('resource_contents', 'value'),
        # Required values in resourceblock.resourcecopy
        State('library_id', 'value'),
        State('copies_total', 'value'),
        State('copies_type1', 'value'),
        State('copies_type2', 'value'),
        State('copies_type3', 'value'),
    ]
)

def catalog(btn, user_id, password,
        existing_title, title, callnum, type, authors,
        subjt1, subjt2, subjt3, date, ed, lang, collect, pub,
        set, vol, series, isbn, issn, desc, contents,
        library, copies, copiest1, copiest2, copiest3):
    ctx = dash.callback_context
    if ctx.triggered:
        eventid = ctx.triggered[0]['prop_id'].split('.')[0]
        if eventid == 'confirmcatalog_btn' and btn:
            color = 'warning'
            text = "Please enter your password."
            is_open = False
            if password == None or password == '': is_open = True
            else:
                sql = """SELECT user_lname AS lname
                    FROM userblock.registereduser
                    WHERE user_id = %s AND user_password = %s;"""
                values = [user_id, password]
                cols = ['lname']
                df = db.querydatafromdatabase(sql, values, cols)
                if df.shape[0] == 0:
                    color = 'danger'
                    text = "Incorrect password"
                    is_open = True
                else:
                    color = 'success'
                    text = "Resource cataloged"
                    is_open = True
                    if existing_title == None or existing_title == '':
                        sql = """INSERT INTO resourceblock.resourcetitles (call_num, resource_title, resource_edition, resourcetype_id, language_id, collection_id, publisher_id,
                            copyright_date, subj_tier1_id, subj_tier2_id, subj_tier3_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
                        values = [callnum, title, ed, type, lang, collect, pub, date, subjt1, subjt2, subjt3]
                        db.modifydatabase(sql, values)
            return [color, text, is_open]
        else: raise PreventUpdate
    else: raise PreventUpdate

layout = [
    dbc.Row(
        [
            cm.sidebar,
            dbc.Col(
                [
                    html.H1("Resource record", id = 'header'),
                    dbc.Row(
                        dbc.Col(
                            html.P(
                                """If this title is already registered in LÁRA,
                                you can select it in the dropdown menu below."""
                            ),
                            width = 11
                        )
                    ),
                    dbc.Row(
                        [
                            #dbc.Label("Title name", width = 2),
                            dbc.Col(
                                dcc.Dropdown(
                                    #type = 'text',
                                    id = 'existing_titles',
                                    placeholder = 'Title name'
                                ), width = 11 #9
                            ),
                        ], className = 'mb-3'
                    ),
                    dbc.Form(
                        [
                            html.Div(
                                [
                                    dbc.Alert(
                                        id = 'catalog_alert',
                                        is_open = False,
                                        dismissable = True,
                                        duration = 5000
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            html.P(
                                                ["""If the title is not found above (or if you're cataloging a new edition), you can enter it below."""]
                                            ),
                                            width = 11
                                        )
                                    ),
                                    dbc.Row(
                                        [
                                            #dbc.Label("Title name", width = 2),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'text',
                                                    id = 'resource_title',
                                                    placeholder = 'Title name'
                                                ), width = 11
                                            )
                                        ], className = 'mb-3'
                                    ),
                                    html.Hr(),
                                    html.H3("Title Information"),
                                    dbc.Row(
                                        [
                                            dbc.Label("Call number", className = 'mb-3 col-sm-4 col-lg-2'),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'text',
                                                    id = 'call_num',
                                                    placeholder = 'R-AAA-BBBB-YYYY',
                                                    disabled = True
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                            dbc.Label("Resource type", className = 'mb-3 col-sm-4 col-lg-3'),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'resourcetype_id',
                                                    placeholder = 'Select resource type...'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            )
                                        ], #className = 'mb-3'
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
                                    dbc.Form(
                                        [
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
                                                        ), className = 'mb-3 col-sm-11 col-lg-3'
                                                    ),
                                                    dbc.Col(
                                                        dbc.Input(
                                                            type = 'text',
                                                            id = 'author_fname',
                                                            placeholder = 'First name'
                                                        ), className = 'mb-3 col-sm-11 col-lg-3'
                                                    ),
                                                    dbc.Col(
                                                        dbc.Input(
                                                            type = 'text',
                                                            id = 'author_mname',
                                                            placeholder = 'Middle name'
                                                        ), className = 'mb-3 col-sm-11 col-lg-3'
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            "Register",
                                                            id = 'newauthor_btn',
                                                            style = {'width' : '100%'}
                                                        ), className = 'mb-3 col-sm-11 col-lg-2'
                                                    )
                                                ], #className = 'mb-3'
                                            )
                                        ]
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
                                                className = 'mb-3 col-sm-11 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'subj_tier1_id'
                                                ), className = 'mb-3 col-sm-11 col-lg-9'
                                            ),
                                            dbc.Tooltip(
                                                """Level 1 refers to the hundreds digit of the resource's subject classification. (E.g., 100, 200, 300.)""",
                                                target = 'subj_tier1_label'
                                            ),
                                        ], #className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Level 2 Class",
                                                id = 'subj_tier2_label',
                                                className = 'mb-3 col-sm-11 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'subj_tier2_id',
                                                    #disabled = True
                                                ), className = 'mb-3 col-sm-11 col-lg-9'
                                            ),
                                            dbc.Tooltip(
                                                """Level 2 refers to the tens digit of the resource's subject classification. (E.g., 110, 120, 130.)""",
                                                target = 'subj_tier2_label'
                                            ),
                                        ], #className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Level 3 Class",
                                                id = 'subj_tier3_label',
                                                className = 'mb-3 col-sm-11 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'subj_tier3_id',
                                                    #disabled = True
                                                ), className = 'mb-3 col-sm-11 col-lg-9'
                                            ),
                                            dbc.Tooltip(
                                                """Level 3 refers to the ones digit of the resource's subject classification. (E.g., 110, 111, 112.)""",
                                                target = 'subj_tier3_label'
                                            ),
                                        ], #className = 'mb-3'
                                    ),
                                    #html.Hr(),
                                    #html.H5("Title Information"),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Copyright date",
                                                id = 'copyright_date_label',
                                                className = 'mb-3 col-sm-4 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dcc.DatePickerSingle(
                                                    id = 'copyright_date',
                                                    placeholder = 'MM/DD/YYYY',
                                                    month_format = 'MMM Do, YYYY',
                                                    clearable = True,
                                                    style = {'width' : '100%'}
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
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
                                                className = 'mb-3 col-sm-4 col-lg-3'
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'number',
                                                    min = 0,
                                                    id = 'resource_edition',
                                                    placeholder = 'Example: 1, 2, 3',
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                        ], className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Language",
                                                className = 'mb-3 col-sm-4 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'language_id',
                                                    placeholder = 'Select language...'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                            dbc.Label(
                                                "Collection",
                                                className = 'mb-3 col-sm-4 col-lg-3'
                                            ),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    id = 'collection_id',
                                                    placeholder = 'Select collection...'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                        ], #className = 'mb-3'
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
                                    dbc.Form(
                                        [
                                            dbc.Row(
                                                dbc.Col(
                                                    html.P(
                                                        ["""If the publisher of this resource is not found above, you can register them here first."""]
                                                    ),
                                                    width = 11
                                                )
                                            ),
                                            dbc.Row(
                                                [
                                                    #dbc.Label("Publisher information", width = 2),
                                                    dbc.Col(
                                                        dbc.Input(
                                                            type = 'text',
                                                            id = 'publisher_name',
                                                            placeholder = 'Publisher name'
                                                        ), className = 'mb-3 col-sm-11 col-lg-6'
                                                    ),
                                                    dbc.Col(
                                                        dbc.Input(
                                                            type = 'text',
                                                            id = 'publisher_loc',
                                                            placeholder = 'Publisher city/state/country'
                                                        ), className = 'mb-3 col-sm-11 col-lg-3'
                                                    ),
                                                    dbc.Col(
                                                        dbc.Button(
                                                            "Register",
                                                            id = 'newpublisher_btn',
                                                            style = {'width' : '100%'}
                                                        ), className = 'mb-3 col-sm-11 col-lg-2'
                                                    )
                                                ], #className = 'mb-3'
                                            )
                                        ]
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
                                    )
                                ], id = 'title_information'
                            ),
                            html.Hr(),
                            html.Div(
                                [
                                    html.H3("Set Information"),
                                    dbc.Row(
                                        dbc.Col(
                                            html.P(
                                                """If a specific set of this title (e.g. volume, number, et cetera) is already registered in LÁRA
                                                and you only wish to add copies to this set, you can select it in the dropdown menu below."""
                                            ),
                                            width = 11
                                        )
                                    ),
                                    dbc.Row(
                                        [
                                            #dbc.Label("Title name", width = 2),
                                            dbc.Col(
                                                dcc.Dropdown(
                                                    #type = 'text',
                                                    id = 'existing_sets',
                                                    placeholder = 'Set information'
                                                ), width = 11 #9
                                            ),
                                        ], className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        dbc.Col(
                                            html.P(
                                                """Otherwise, please input all applicable details below."""
                                            ),
                                            width = 11
                                        )
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Volume number",
                                                className = 'mb-3 col-sm-4 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'number',
                                                    min = 0,
                                                    id = 'resource_volnum',
                                                    placeholder = 'Volume number'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                            dbc.Label(
                                                "Series number",
                                                className = 'mb-3 col-sm-4 col-lg-3'
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'number',
                                                    min = 0,
                                                    id = 'resource_seriesnum',
                                                    placeholder = 'Series number'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                        ],
                                        #className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "ISBN (if applicable)",
                                                className = 'mb-3 col-sm-4 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'text',
                                                    id = 'resource_isbn',
                                                    placeholder = 'ISBN'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                            dbc.Label(
                                                "ISSN (if applicable)",
                                                className = 'mb-3 col-sm-4 col-lg-3'
                                            ),
                                            dbc.Col(
                                                dbc.Input(
                                                    type = 'text',
                                                    id = 'resource_issn',
                                                    placeholder = 'ISSN'
                                                ), className = 'mb-3 col-sm-7 col-lg-3'
                                            ),
                                        ],
                                        #className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Resource description",
                                                className = 'mb-3 col-sm-11 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dbc.Textarea(
                                                    id = 'resource_desc',
                                                    placeholder = 'Enter description here.'
                                                ), className = 'mb-3 col-sm-11 col-lg-9'
                                            )
                                        ],
                                        #className = 'mb-3'
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Label(
                                                "Table of contents",
                                                className = 'mb-3 col-sm-11 col-lg-2'
                                            ),
                                            dbc.Col(
                                                dbc.Textarea(
                                                    id = 'resource_contents',
                                                    placeholder = 'Enter table of contents here.'
                                                ), className = 'mb-3 col-sm-11 col-lg-9'
                                            )
                                        ],
                                        #className = 'mb-3'
                                    )
                                ], id = 'set_information'
                            ),
                            html.Hr(),
                            html.Div(
                                [
                                    html.H3("Copy Information"),
                                    dbc.Col(
                                        html.P("""Set the number of copies (and circulation types of each copy) for your library below.
                                               Unclassified copies are automatically set for regular circulation.
                                               Accession numbers for each copy are automatically generated."""),
                                        width = 11
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    dcc.Dropdown(
                                                        id = 'library_id',
                                                        placeholder = 'Select library...'
                                                    ),
                                                    dbc.FormText("Library"),
                                                ], className = 'mb-3 col-sm-9 col-lg-5'
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        type = 'number',
                                                        id = 'copies_total',
                                                        min = 1,
                                                        value = 1
                                                    ),
                                                    dbc.FormText("Total number"),
                                                ], className = 'mb-3 col-sm-2 col-lg-1'
                                            ),
                                            dbc.Label("Copies per classification type", className = 'mb-3 col-sm-5 col-lg-2'),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        type = 'number',
                                                        id = 'copies_type2',
                                                        min = 0,
                                                        value = 0
                                                    ),
                                                    dbc.FormText("Room-use only"),
                                                ], className = 'mb-3 col-sm-2 col-lg-1'
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        type = 'number',
                                                        id = 'copies_type3',
                                                        min = 0,
                                                        value = 0
                                                    ),
                                                    dbc.FormText("Reserve books"),
                                                ], className = 'mb-3 col-sm-2 col-lg-1'
                                            ),
                                            dbc.Col(
                                                [
                                                    dbc.Input(
                                                        type = 'number',
                                                        id = 'copies_type1',
                                                        min = 0,
                                                        value = 0,
                                                        disabled = True
                                                    ),
                                                    dbc.FormText("Regular circulation"),
                                                ], className = 'mb-3 col-sm-2 col-lg-1'
                                            ),
                                        ], #className = 'mb-3'
                                    )
                                ], id = 'copy_information'
                            )
                        ],
                        id = 'resource_catalog'
                    ),
                    dbc.ModalFooter(
                        [
                            dbc.Button(
                                "Catalog", color = 'primary', id = 'catalog_btn'
                            ),
                        ]
                    )
                ]
            )
        ]
    ),
    dbc.Modal(
        [
            dbc.ModalHeader(html.H4('Confirm details')),
            dbc.ModalBody(
                [
                    html.Div(id = 'catalog_modalbody'),
                    html.Hr(),
                    dbc.Alert(
                        id = 'catalogconfirm_alert',
                        is_open = False,
                        dismissable = True,
                        duration = 5000),
                    html.H6("To catalog this resource, please enter your password."),
                    dbc.Row(
                        dbc.Col(
                            dbc.Input(type = 'password', id = 'catalog_password', placeholder = 'Password')
                        ), className = 'mb-3'
                    )
                ]
            ),
            dbc.ModalFooter(
                dbc.Button("Confirm", id = 'confirmcatalog_btn')
            )
        ],
        centered = True,
        scrollable = True,
        id = 'catalog_confirmationmodal',
        backdrop = 'static'
    )
]