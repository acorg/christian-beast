from unittest import TestCase
from six import assertRaisesRegex, StringIO, PY3
from math import log10
from xml.etree.ElementTree import tostring

from cbeast.matrix import Matrix

ENCODING = 'unicode' if PY3 else None


class TestMatrix(TestCase):
    """
    Tests for the cbeast.matrix.Matrix class.
    """

    def testEmpty(self):
        """
        If the CSV input is empty, a ValueError must be raised.
        """
        csv = StringIO()
        error = '^No input CSV data found\.$'
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testHeaderOnly(self):
        """
        If the CSV input only has a header line, a ValueError must be raised.
        """
        csv = StringIO('A, B, C\n')
        error = '^No taxa \(rows\) found in input CSV\.$'
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testRowWithTooManyFields(self):
        """
        If the CSV input has a row with more fields than there are features
        (columns), a ValueError must be raised.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name, 3, 4, 5, 6\n')
        error = ('^Input row 2 contains 4 value fields, but there were 3 '
                 'feature \(column\) headers$')
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testRowWithTooFewFields(self):
        """
        If the CSV input has a row with fewer fields than there are features
        (columns), a ValueError must be raised.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name, 3\n')
        error = ('^Input row 2 contains 1 value fields, but there were 3 '
                 'feature \(column\) headers$')
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testNonNumerical(self):
        """
        If the CSV input has a row with a field that is not numerical, a
        ValueError must be raised.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name, 2, 3, hello\n')
        if PY3:
            error = "^could not convert string to float: ' hello'$"
        else:
            error = '^could not convert string to float: hello$'
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testRepeatedFeatureName(self):
        """
        If the CSV input has a repeated feature name, a ValueError must be
        raised.
        """
        csv = StringIO('Ignored, A, B, A\n'
                       'name, 2, 3, hello\n')
        error = "^Feature name 'A' appears more than once$"
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testRepeatedTaxaName(self):
        """
        If the CSV input has a repeated taxa name, a ValueError must be raised.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name, 1, 2, 3\n'
                       'name, 4, 5, 6\n')
        error = "^Taxa name 'name' appears more than once$"
        assertRaisesRegex(self, ValueError, error, Matrix, csv)

    def testFeatureNames(self):
        """
        The feature names must be correctly extracted.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name, 3, 4\n')
        m = Matrix(csv)
        self.assertEqual(['A', 'B'], list(m.features))

    def testTaxaNames(self):
        """
        The taxa names must be correctly extracted.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n')
        m = Matrix(csv)
        self.assertEqual(['name1', 'name2'], list(m.taxa))

    def testFeatureValues(self):
        """
        The feature values must be correctly extracted.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n')
        m = Matrix(csv)
        self.assertEqual([3.0, 5.0], m.features['A'])
        self.assertEqual([4.0, 6.0], m.features['B'])

    def testTaxaValues(self):
        """
        The taxa values must be correctly extracted.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n')
        m = Matrix(csv)
        self.assertEqual([3.0, 4.0], m.taxa['name1'])
        self.assertEqual([5.0, 6.0], m.taxa['name2'])

    def testDistanceMatrixForUnknownFeature(self):
        """
        A KeyError must be raised if an attempt is made to get a distance
        matrix for an unknown feature.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name1, 1, 2, 3\n'
                       'name2, 4, 5, 6\n')
        m = Matrix(csv)
        error = "^'XXX'$"
        assertRaisesRegex(self, KeyError, error, m.distanceMatrix, 'XXX')

    def testDistanceMatrix(self):
        """
        It must be possible to produce a distance matrix for a feature.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n'
                       'name3, 7, 8\n')
        m = Matrix(csv)
        self.assertEqual(
            [[0.0, -2.0, -4.0],
             [2.0, 0.0, -2.0],
             [4.0, 2.0, 0.0]],
            m.distanceMatrix('A', logged=False))

    def testDistanceMatrixLogged(self):
        """
        It must be possible to produce a distance matrix for a feature
        whose values have been logged.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n'
                       'name3, 7, 8\n')
        m = Matrix(csv)
        L3 = log10(3.0)
        L5 = log10(5.0)
        L7 = log10(7.0)

        self.assertEqual(
            [[0.0, L3 - L5, L3 - L7],
             [L5 - L3, 0.0, L5 - L7],
             [L7 - L3, L7 - L5, 0.0]],
            m.distanceMatrix('A', logged=True))

    def testDistanceMatrixLoggedByDefault(self):
        """
        The distance matrices produced for a feature must have their values
        logged by default.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n'
                       'name3, 7, 8\n')
        m = Matrix(csv)
        L3 = log10(3.0)
        L5 = log10(5.0)
        L7 = log10(7.0)

        self.assertEqual(
            [[0.0, L3 - L5, L3 - L7],
             [L5 - L3, 0.0, L5 - L7],
             [L7 - L3, L7 - L5, 0.0]],
            m.distanceMatrix('A'))

    def testUpperDiagonalForUnknownFeature(self):
        """
        A KeyError must be raised if an attempt is made to get the upper
        diagonal for an unknown feature.
        """
        csv = StringIO('Ignored, A, B, C\n'
                       'name1, 1, 2, 3\n'
                       'name2, 4, 5, 6\n')
        m = Matrix(csv)
        error = "^'XXX'$"
        assertRaisesRegex(self, KeyError, error, m.upperDiagonal, 'XXX')

    def testUpperDiagonal(self):
        """
        It must be possible to produce the upper diagonal of a distance matrix
        for a feature.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n'
                       'name3, 7, 8\n')
        m = Matrix(csv)
        self.assertEqual([-2.0, -4.0, -2.0],
                         m.upperDiagonal('A', logged=False))

    def testUpperDiagonalAsXML(self):
        """
        It must be possible to produce XML for the upper diagonal of a
        distance matrix for a feature.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 6\n'
                       'name3, 7, 8\n')
        m = Matrix(csv)
        element = m.upperDiagonalAsXML('A', logged=False)
        self.assertEqual(
            ('<xxx><value>-2.0</value><value>-4.0</value>'
             '<value>-2.0</value></xxx>'),
            tostring(element, encoding=ENCODING))

    def testAllfeaturesAsXML(self):
        """
        It must be possible to produce XML for the upper diagonal of the
        distance matrices for all features.
        """
        csv = StringIO('Ignored, A, B\n'
                       'name1, 3, 4\n'
                       'name2, 5, 7\n'
                       'name3, 7, 9\n')
        m = Matrix(csv)
        element = m.allFeaturesAsXML(logged=False)
        self.assertEqual(
            ('<xxx>'
             '<!--A-->'
             '<feature>'
             '<value>-2.0</value><value>-4.0</value><value>-2.0</value>'
             '</feature>'
             '<!--B-->'
             '<feature>'
             '<value>-3.0</value><value>-5.0</value><value>-2.0</value>'
             '</feature>'
             '</xxx>'),
            tostring(element, encoding=ENCODING))
