import unittest

# The module we're testing.
import db

# Additional modules
import os
import tempfile

class TestMemoryDB(unittest.TestCase):

    def setUp(self):
        self.db = db.DB(":memory:")

    def tearDown(self):
        self.db.close()


class TestDBConsistency(TestMemoryDB):
    """Tests relating to data consistency"""

    def setUp(self):
        super().setUp()
        self.db.create_schema()
        self.db.define_anchor(displayname="A", path="a.txt", address="|A|",
                names={"Ah", "Ahaa!"})
        self.db.define_anchor(displayname="B", path="b.txt", address="|B|",
                names={"Babe", "Bay, Michael"})
        self.db.define_anchor(displayname="Other A", path="a.txt", address="|Other A|",
                names={"Ah", "Ahaahahah!"})

    def test_uniqe_anchor(self):
        with self.assertRaisesRegex(db.sqlite3.IntegrityError,
                "UNIQUE constraint failed:.+"):
            self.db.define_anchor("A2", "a.txt", "|A|")

    def test_find_anchors(self):
        results = set(self.db.find_anchors("Ah"))
        self.assertEqual(len(results), 2)

    def test_find_anchors_displayname(self):
        """Finding by displayname should also work."""
        r1 = set(self.db.find_anchors("B"))
        r2 = set(self.db.find_anchors("Babe"))
        self.assertEqual(r1, r2)

    def test_find_anchors_case(self):
        """Anchor finding should be case insensitive."""
        r1 = set(self.db.find_anchors("B"))
        r2 = set(self.db.find_anchors("b"))  # Was never entered like that.
        self.assertEqual(r1, r2)

    def test_get_anchor_names(self):
        names = set(self.db.get_anchor_names("a.txt", "|A|"))
        self.assertEqual(names, {"A", "Ah", "Ahaa!"})


class TestDBSchema(TestMemoryDB):
    """Tests relating to database schema"""

    def test_schema_recreation(self):
        """Raise exception if trying to create the schema twice."""
        self.db.create_schema()
        with self.assertRaisesRegex(db.sqlite3.OperationalError,
                                    r"table \w+ already exists"):
            self.db.create_schema()

    def test_store_before_schema(self):
        """Storing stuff before the schema is created doesn't work."""
        with self.assertRaisesRegex(db.sqlite3.OperationalError,
                                    r"no such table: \w+"):
            self.db.define_anchor("A", "somefile.txt", "def A")


class TestFileDB(unittest.TestCase):
    """Test DB functionality where filesystem access is important."""

    def setUp(self):
        self.dbpath = self.tempfilename()
        self.db     = db.DB(dbname=self.dbpath)

        self.assertTrue(os.path.exists(self.dbpath))

        self.db.create_schema()

    def tearDown(self):
        """File must exist before and not exist after destruction."""
        self.assertTrue(os.path.exists(self.db.dbname))
        self.db.destroy()
        self.assertFalse(os.path.exists(self.db.dbname))

    def tempfilename(self):
        """Create a unique temporary filename to be used as a database file path."""
        with tempfile.NamedTemporaryFile(delete=True) as f:
            name = f.name
        return name

    def test_path(self):
        """The ``path`` property must be the same as the one given in the creation argument."""
        self.assertEqual(self.db.path, self.dbpath)

    @unittest.skip
    def test_persistence(self):
        """Test if data persists after opening and closing the database."""

        name = "A"
        apath = "a.txt"
        adef  = "define A"

        self.db.define_anchor(name, apath, adef)
        self.db.close()

        # Time passes.
        # OK, enough time passed, let's re-open the database

        self.db = db.DB(dbname=self.dbpath)
        result = self.db.get_anchor(apath, adef)

        self.assertEqual(tuple(result), (name, apath, adef))
