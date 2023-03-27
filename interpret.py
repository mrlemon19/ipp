# interpret.py 2. cast projektu do IPP
# @author: Jakub Lukas, xlukas18

import sys

if __name__ == "__main__":
    for i in sys.argv:
        if i == "--help":
            print("interpret.py")
            print("Skript pro interpretaci XML reprezentace programu v IPPcode23.")
            print("udage: python3 interpret.py [--help] [--source=file] [--input=file]")
            print("     --help vypise napovedu")
            print("     --source=file zdrojovy kod v IPPcode23")
            print("     --input=file vstupni soubor pro program")
            print("     alespon jeden z parametru source a input musi byt zadany")
            print("     pri absenci jednoho z parametru je source/input nacitan ze standardniho vstupu")
            print("\n")
            exit(0)
