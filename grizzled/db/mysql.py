# $Id$

"""
MySQL extended database driver.
"""

# ---------------------------------------------------------------------------
# Imports
# ---------------------------------------------------------------------------

import os
import sys
import re

from grizzled.db.base import DBDriver, Error, Warning

# ---------------------------------------------------------------------------
# Exports
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Classes
# ---------------------------------------------------------------------------

class MySQLDriver(DBDriver):
    """DB Driver for MySQL, using the MySQLdb DB API module."""

    TYPE_RE = re.compile('([a-z]+)(\([0-9]+\))?')

    def get_import(self):
        import MySQLdb
        return MySQLdb

    def get_display_name(self):
        return "MySQL"

    def do_connect(self,
                   host="localhost",
                   port=None,
                   user="sa",
                   password="",
                   database="default"):
        dbi = self.get_import()
        return dbi.connect(host=host, user=user, passwd=password, db=database)

    def get_table_metadata(self, table, cursor):
        self._ensure_valid_table(cursor, table)
        dbi = self.get_import()
        cursor.execute('DESC %s' % table)
        rs = cursor.fetchone()
        results = []
        while rs is not None:
            column = rs[0]
            coltype = rs[1]
            null = False if rs[2] == 'NO' else True

            match = self.TYPE_RE.match(coltype)
            if match:
                coltype = match.group(1)
                size = match.group(2)
                if size:
                    size = size[1:-1]
                if coltype in ['varchar', 'char']:
                    max_char_size = size
                    precision = None
                else:
                    max_char_size = None
                    precision = size

            results += [(column, coltype, max_char_size, precision, 0, null)]
            rs = cursor.fetchone()

        return results

    def get_index_metadata(self, table, cursor):
        self._ensure_valid_table(cursor, table)
        dbi = self.get_import()
        cursor.execute('SHOW INDEX FROM %s' % table)
        rs = cursor.fetchone()
        result = []
        columns = {}
        descr = {}
        while rs is not None:
            name = rs[2]
            try:
                columns[name]
            except KeyError:
                columns[name] = []

            columns[name] += [rs[4]]

            # Column 1 is a "non-unique" flag.

            if (not rs[1]) or (name.lower() == 'primary'):
                description = 'Unique'
            else:
                description = 'Non-unique'
            if rs[10] is not None:
                description += ', %s index' % rs[10]
            descr[name] = description
            rs = cursor.fetchone()

        names = columns.keys()
        names.sort()
        for name in names:
            result += [(name, columns[name], descr[name])]

        return result

    def get_tables(self, cursor):
        cursor.execute('SHOW TABLES')
        table_names = []
        rs = cursor.fetchone()
        while rs is not None:
            table_names += [rs[0]]
            rs = cursor.fetchone()

        return table_names
