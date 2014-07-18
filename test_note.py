#!/bin/env python3

import note
import unittest

import random

class TestAnchorParser(unittest.TestCase):

    def test_parse_simple(self):
        """Parse a simple anchor definition."""
        anchorstring = "Wait. |This is an anchor|."
        self.help_parse(anchorstring, {
            'pos': 6,
            'start': '|',
            'end': '|',
            'text': 'This is an anchor'
            })

    def test_parse_escape(self):
        """Parse an anchor definition with escaped characters."""
        anchorstring = "\|This is |an \nanchor\| that goes on|."
        self.help_parse(anchorstring, {
            'pos': 10,
            'text': 'an \nanchor\| that goes on'
            })

    def help_parse(self, text, *expectations):
        """Parses ``text``, compares to *expectations.

        Each expectation is a dictionary. ``text`` must 
        yield as many ``Anchor``s as there are expectations. 
        Order of expectations matters. For each expectation:

        - anchor must have the same attributes as the 
          corresponding expectation.
        - The concatenation of the ``start``, ``text`` and 
          ``end`` attributes of the anchor must be found in 
          ``text``.
        """
        anchors = list(note.AnchorParser().parse(text))
        self.assertEqual(len(anchors), len(expectations))
        for n, expectation in enumerate(expectations):
            a = anchors[n]
            for key, value in expectation.items():
                self.assertEqual(a.__dict__[key], value)
            self.assertIn(a.start+a.text+a.end, text)

class TestAnchorTagRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = note.AnchorTagRenderer()

    def tearDown(self):
        del self.renderer

    def test_render_anchor(self):
        """Render a single anchor to a tagfile line."""
        anchor = note.Anchor(
            path = 'testfile.txt',
            text = '2  spaces, slash/es \nnewline',
            start = '|', end = '|')
        line = self.renderer.render_anchor(anchor)
        expectation = ('2 spaces, slash/es newline\t'
                       'testfile.txt\t'
                      r'/|2  spaces, slash\/es \nnewline|/'+'\n')
        self.assertEqual(line, expectation)

    def test_render_anchor_exception(self):
        """Throw an Error if a required key is missing."""
        default = {
            'start': '|', 'end': '|',
            'text': 'blah', 'path': 'blub.txt'
            }
        for dont_use in default.keys():
            missing = {k:default[k] for k in default if not k == dont_use}
            a = note.Anchor(**missing)
            self.assertRaises(AttributeError,
                    self.renderer.render_anchor, a)

    def test_render_anchors(self):
        """When rendering multiple tag lines, they must be ordered."""

        chars = "abcdefghijklmnopqrstuvwxyz"
        def a(char, p):
            return note.Anchor(path=p, text=char, start='|', end='|')

        anchors = [
            a('a', 'p'),
            a('c', 'p'),
            a('!', 'p'),
            a('b', 'p'),
            ]
        expectation = [
            '!\tp\t/|!|/\n',
            'a\tp\t/|a|/\n',
            'b\tp\t/|b|/\n',
            'c\tp\t/|c|/\n',
            ]
        for n in range(3):  # Test three permutations
            random.shuffle(anchors)
            lines = self.renderer.render_anchors(anchors)
            self.assertEqual(lines, expectation)


if __name__ == '__main__':
    unittest.main()
