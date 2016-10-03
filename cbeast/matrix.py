import csv
from math import log10
from collections import OrderedDict

from xml.etree.ElementTree import Element, SubElement, Comment


class Matrix(object):
    """
    Read and manage a matrix of numeric taxa features.

    @param csvfp: A file pointer, whose contents are CSV.
    @raise ValueError: If a feature or taxa name is repeated, or if
        a CSV row has too many/few values, or if there is not enough
        CSV data.
    """

    def __init__(self, csvfp):
        taxa = OrderedDict()
        features = OrderedDict()

        for row, fields in enumerate(csv.reader(csvfp), start=1):
            if row == 1:
                for featureName in map(str.strip, fields[1:]):
                    if featureName in features:
                        raise ValueError(
                            'Feature name %r appears more than once' %
                            featureName)
                    else:
                        features[featureName] = []
                nFeatures = len(features)
            else:
                if len(fields) - 1 != nFeatures:
                    raise ValueError(
                        'Input row %d contains %d value fields, but there '
                        'were %d feature (column) headers' %
                        (row, len(fields) - 1, nFeatures))

                taxaName = fields[0].strip()
                if taxaName in taxa:
                    raise ValueError(
                        'Taxa name %r appears more than once' % taxaName)
                else:
                    taxa[taxaName] = []

                for featureName, value in zip(features,
                                              map(float, fields[1:])):
                    taxa[taxaName].append(value)
                    features[featureName].append(value)

        if not features:
            raise ValueError('No input CSV data found.')

        if not taxa:
            raise ValueError('No taxa (rows) found in input CSV.')

        self.taxa = taxa
        self.features = features

    def distanceMatrix(self, featureName, logged=True):
        """
        Create a distance matrix for a feature.

        @param featureName: A C{str} feature (column) name.
        @param logged: If C{True}, log (base 10) all values before calculating
            distances.
        @raise KeyError: If C{featureName} is unknown.
        @return: A square distance matrix. Row/column order is given by the
            ordering of the taxa in C{self.taxa}.
        """
        if logged:
            scaledvalues = []
            for value in self.features[featureName]:
                try:
                    scaledvalues.append(log10(value))
                except ValueError:
                    scaledvalues.append(0.0)
        else:
            scaledvalues = self.features[featureName]
        values = dict(zip(self.taxa, scaledvalues))
        result = []
        for taxaName1 in self.taxa:
            row = []
            for taxaName2 in self.taxa:
                row.append(values[taxaName1] - values[taxaName2])
            result.append(row)
        return result

    def upperDiagonal(self, featureName, logged=True):
        """
        Calculate the upper diagonal of a distance matrix for a feature.

        @param featureName: A C{str} feature (column) name.
        @param logged: If C{True}, log (base 10) all values before calculating
            distances.
        @raise KeyError: If C{featureName} is unknown.
        @return: A one-dimensional list of values from the upper diagonal of
            the distance matrix for the feature.
        """
        result = []
        nTaxa = len(self.taxa)
        dm = self.distanceMatrix(featureName, logged)
        for row in range(nTaxa):
            for col in range(row + 1, nTaxa):
                result.append(dm[row][col])
        return result

    def upperDiagonalAsXML(self, featureName, elementName='xxx',
                           logged=True):
        """
        Calculate the upper diagonal of a distance matrix for a feature as XML.

        @param featureName: A C{str} feature (column) name.
        @param elementName: The C{str} name of the XML element tag to return.
        @param logged: If C{True}, log (base 10) all values before calculating
            distances.
        @raise KeyError: If C{featureName} is unknown.
        @return: An XML C{Element} whose children have the values from the
            upper diagonal of the feature named by C{featureName}.
        """
        result = Element(elementName)
        for value in map(str, self.upperDiagonal(featureName, logged)):
            SubElement(result, 'value').text = value
        return result

    def allFeaturesAsXML(self, elementName='xxx', logged=True):
        """
        Calculate the upper diagonal of a distance matrix for all feature as
        XML.

        @param elementName: The C{str} name of the XML element tag to return.
        @param logged: If C{True}, log (base 10) all values before calculating
            distances.
        @return: An XML C{Element} whose children are elements with the values
        from the upper diagonals of all features.
        """
        result = Element(elementName)
        for featureName in self.features:
            result.append(Comment(featureName))
            child = self.upperDiagonalAsXML(
                featureName, elementName='feature', logged=logged)
            result.append(child)
        return result
