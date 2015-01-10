"""Provides Database functions."""

import os
import sqlite3

from parsing.anchors import Anchor

from util import debug

def collate_lowercase(s1, s2):
    s1 = s1.lower()
    s2 = s2.lower()
    if s1 < s2:
        return -1
    elif s1 == s2:
        return 0
    else:
        return 1

class AttributeRow(sqlite3.Row):
    """Allows access via both row.name and row['name']."""
    def __getattr__(self, name):
        return self[name]

class DB:
    dbname = "notes.db"

    def __init__(self, dbname=None):
        if dbname:
            self.dbname = dbname
        self.conn = sqlite3.connect(self.dbname)
        self.conn.row_factory = AttributeRow
        self.conn.create_collation("collate_lowercase", collate_lowercase)

    def close(self):
        self.conn.close()

    @property
    def path(self):
        return self.conn.execute("PRAGMA database_list").fetchone()[2]

    def destroy(self):
        """Delete the database file."""
        dbpath = self.path
        self.close()
        os.remove(dbpath)


    # Schema related functions and properties #
    @property
    def _schemafile_path(self):
        """Absolute path to the schema file."""
        directory = os.path.dirname(__file__)  # only works if not toplevel, so only test with 'import db'
        return os.path.join(directory, "schema.sql")

    def create_schema(self):
        """Create the database schema."""
        with open(self._schemafile_path) as f:
            sql = f.read()
        self.conn.executescript(sql)


    # Data Input and Output #
    def define_anchor(self, displayname, path, address, names=None):
        """Put an anchor into the database.

        If given, ``names`` should be an iterable of strings
        by which to also find this anchor (in addition to ``displayname``,
        which will be the preferred one).

        Raises an ``sqlite3.IntegrityError`` when this combination of
        ``path`` and ``address`` already exists.
        """
        with self.conn:
            cur = self.conn.execute(
                    'INSERT OR ROLLBACK INTO displaynames(path,address,displayname) VALUES (?,?,?)',
                    [path, address, displayname])

            names = set(names) if names else set()
            names.add(displayname)
            cur.executemany(
                    'INSERT OR ROLLBACK INTO names(name, path, address) VALUES (?,?,?)',
                    ((name, path, address) for name in names))
        return

    def find_anchors(self, name):
        """Find an anchor by name.

        Returs a Row object with ``displayname``,
        ``path``, and ``address`` attributes.
        """
        cur = self.conn.execute('''SELECT displayname, path, address
                                   FROM anchors WHERE name=?''', (name,))
        return cur.fetchall()

    def get_anchor_names(self, path, address):
        """Find all other names for given anchor.

        >>> exdb = DB(":memory:")
        >>> exdb.create_schema()
        >>> exdb.define_anchor("A", "a.txt", "|A|", {"AAA", "Aaaaaa"})

        >>> list(sorted(exdb.get_anchor_names("a.txt", "|A|")))
        ['A', 'AAA', 'Aaaaaa']
        """
        cur = self.conn.execute('''SELECT name FROM anchors
                                   WHERE path=? AND address=?''',
                                   (path, address))
        return (row.name for row in cur.fetchall())
