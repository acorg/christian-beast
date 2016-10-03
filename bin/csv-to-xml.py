#!/usr/bin/env python

import argparse
import sys
from xml.etree.ElementTree import ElementTree

from cbeast.matrix import Matrix


parser = argparse.ArgumentParser(description='Convert CSV to XML for BEAST')

parser.add_argument(
    '--fragment', action='store_true', default=False,
    help='If specified, output only an XML fragment (for pasting).')

args = parser.parse_args()

ElementTree(
    Matrix(sys.stdin).allFeaturesAsXML()).write(
        sys.stdout, encoding='unicode',
        xml_declaration=(not args.fragment))
