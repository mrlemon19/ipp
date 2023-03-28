import sys
import xml.etree.ElementTree as ET
import argparse

# interpret.py 2. cast projektu do IPP
# @author: Jakub Lukas, xlukas18

class instruction:
    def __init__(self, opcode, order):
        self.name: str = opcode
        self.order: int = order

if __name__ == "__main__":

    # zpracovani argumentu
    argParser = argparse.ArgumentParser()
    argParser.add_argument('--source', help = 'source XML file in IPPcode23')
    argParser.add_argument("--input", help = "input file")
    args = argParser.parse_args()

    sourceFile = args.source
    inputFile = args.input

    # xml parser
    tree = ET.parse(sourceFile)
    root = tree.getroot()

    # print xml file
    for child in root:
        print(child.tag, child.attrib)
