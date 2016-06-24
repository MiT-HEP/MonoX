#!/usr/bin/env python

import os
import sys
import shutil
import sqlite3

thisdir = os.path.dirname(os.path.realpath(__file__))
basedir = os.path.dirname(thisdir)
sys.path.append(basedir)
import config

try:
    sname = sys.argv[1]
except IndexError:
    sname = None

try:
    field = sys.argv[2]
except IndexError:
    field = None

try:
    value = sys.argv[3]
except IndexError:
    value = None

conn = sqlite3.connect(basedir + '/data/datasets.db')
db = conn.cursor()

fields = ['title', 'book', 'fullname', 'crosssection', 'nevents', 'sumw', 'lumi', 'comments']
textFields = ['title', 'book', 'fullname', 'comments']
intFields = ['nevents']
floatFields = ['crosssection', 'sumw', 'lumi']

def getRequest(sname, field, value):
    if sname is None:
        print 'Dataset? [.q to quit]'
        sname = sys.stdin.readline().strip()
        if sname == '.q':
            return ('.q', None, None)

    db.execute('SELECT * FROM `datasets` WHERE `name` LIKE ?', (sname,))

    if db.fetchone() is None:
        print 'Unknown dataset', sname
        return (None, field, value)
    
    if field is None:
        print 'Field? [%s]' % ('|'.join(fields))
        field = sys.stdin.readline().strip()
            
    if field not in fields:
        print 'Unknown field', field
        return (sname, None, value)

    if value is None:
        print 'Value?'
        value = sys.stdin.readline().strip()

    try:
        if field in intFields:
            value = int(value)
        elif field in floatFields:
            value = float(value)

    except ValueError:
        print 'Invalid value', value
        return (sname, field, None)
    
    return (sname, field, value)


while True:
    request = getRequest(sname, field, value)

    if request[0] == '.q':
        break

    if None in request:
        if len(sys.argv) > 3:
            break

        else:
            continue

    sname, field, value = request

    db.execute('UPDATE `datasets` SET `{field}` = ? WHERE `name` LIKE ?'.format(field = field), (value, sname))
    conn.commit()

    print 'Success'

    if len(sys.argv) > 3:
        break

    sname = None
    field = None
    value = None

conn.close()
