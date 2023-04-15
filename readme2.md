# Implementační dokumentace k 2. úloze do IPP 2023
## Jméno a příjmení: Jakub Lukáš
## Login: xlukas18

### Popis základní funkcionality
Skript interpret.py je napsaný v jazyce python3.10. Skript bere na vstupu xml reprezentaci kódu v jazyce IPPcode23. Zpracuje vstup a vytvoří jeho interní reprezentaci. Následně se provede interpretace kódu a výsledky se vypíšou na standartní výstup.

### Použití
Skript je spouštěn příkazem `python3.10 interpret.py [--help] [--source=file] [--input=file]`. Argumenty jsou nepovinné. Argument `--help` vypíše nápovědu a skript se ukončí. Argument `--source=file` nastaví soubor `file` jako vstupní kód. Argument `--input=file` nastaví soubor `file` jako vstup programu. Když není zadán argument `--source`, nebo `--input`, je místo něj použit standartní vstup. Skript však musí být spuštěn s alepoń jedním argumentem.

### Použité knihovny a jejich použití
- sys - pro práci s argumenty příkazové řádky
- xml.etree.ElementTree - pro práci s xml
- argparse - pro práci s argumenty příkazové řádky