#!/bin/env python3

import notes
import unittest

import random

class TestAnchorParser(unittest.TestCase):

    def test_parse_simple(self):
        """Parse a simple anchor definition."""
        anchorstring = "Wait. |This is an anchor|."
        self.help_parse(anchorstring, {
            'name': 'This is an anchor'
            })

    def test_parse_escape(self):
        """Parse an anchor definition with escaped characters."""
        anchorstring = "\|This is |an \nanchor\| that goes on|."
        self.help_parse(anchorstring, {
            'name': 'an anchor\| that goes on',
            'definition': '|an \nanchor\| that goes on|'
            })

    def test_parse_multi(self):
        """Parse an anchor with parentheticals."""
        anchorstring = "|((Very) useful) feature|"
        self.help_parse(anchorstring,
            {'name': '((Very) useful) feature',
             'aliases': set(['Very useful feature',
                             'useful feature',
                             'feature'])
            }
        )

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
        anchors = list(notes.AnchorParser().parse(path="blah.txt", txt=text))
        self.assertEqual(len(anchors), len(expectations))
        for n, expectation in enumerate(expectations):
            a = anchors[n]
            for key, value in expectation.items():
                self.assertEqual(a.__dict__[key], value)
            # The following doesn't hold true for multi-valued anchors.
            # But we'll keep it in mind, maybe we can test for something 
            # similar in the future.
            # self.assertIn(a.start+a.text+a.end, text)

class TestAnchorTagRenderer(unittest.TestCase):

    def setUp(self):
        self.renderer = notes.AnchorTagRenderer()

    def tearDown(self):
        del self.renderer

    def test_anchor_to_tags(self):
        """Render a single anchor to a tagfile line."""
        anchor = notes.Anchor(
            name = 'Two spaces, slashes and a newline.',
            path = 'testfile.txt',
            definition = '|2  spaces, slash/es \nnewline|')
        line = list(self.renderer.anchor_to_tags(anchor))
        expectation = [('Two spaces, slashes and a newline.\t'
                       'testfile.txt\t'
                      r'/|2  spaces, slash\/es \nnewline|/'+'\n')]
        self.assertEqual(line, expectation)

    def test_render_anchors(self):
        """When rendering multiple tag lines, they must be ordered."""

        chars = "abcdefghijklmnopqrstuvwxyz"
        def a(char, p):
            return notes.Anchor(path=p, name=char, definition='|'+char+'|')

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
