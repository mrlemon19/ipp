# Projekt do Principy programovacích jazyků a OOP (IPP) na VUT FIT
## autor: Jakub Lukáš

### Zadání
Cílem projektu bylo vytvořit dva skripty sloužící pro interpretaci jakzyka IPPcode23. Analyzátor kódu parse.php v jazyce php8.1 co překládá vstupní kód do xml reprezentace a kontroluje syntaktické a lexikání chyby v kódu. Interpret XML reprezentace interpter.py v jazyce python3.10 co bere ze vstupu xml reprezentaci a provadí samotnou intrepretaci. Skripty jsou podrobně popsány v `readme1.md` (parse.php) a `readme2.md` (interpret.py).

### Jazyk IPPcode23
Jazyk se skládá z jednořádkových instrukcí, každá má 0 až 3 argumenty. Každý program musí na začátku obsahovat hlavičku ".IPPcode23". Jsou podporovány jednořádkové komentáře začínající "\#". Operační kód instrukce a její argumenty jsou od sebe odděleny mezerou, nebo jiným bílým znakem. Instrukční sada se skládá z instrukcí aritmetických (add, mul, ...), logických (or, and, ...), skokových (jump, jumpifeq, label, call, return), zásobníkové (pushs, pops), instrukce pro operace s rámci (createframe, pushframe, ...) a další. Proměnné jsou dynamicky typované a skládají se z označení rámce, znaku "@" a jména proměnné. Rámce jsou tři: TF (Temporary Frame) - dočasný rámec, LF (Local Frame) - lokální rámec a GF - (Global Frame) - Globální rámec. Symboly, které se vyskytují v argumentech instrukcí začínají označením jejich typu, znakem "@" a hodnotou např. "string@Hello\032World", "int@3456", "bool@True", "nil@nil". Null je v IPPcode23 reprezentován symbolem "nil@nil". U typu string je kvuli syntaktickému významu mezer třeba zaměnít mezery za escape sekvenci "\032". Podobně je porřeba u znaky, co mají syntaktický význam v IPPcode23 (např. "\#"), změnit na jejich ascii hodnotu v podobném formátu jako u mezer.

### Ukázka kódu v IPPcode23

. IPPcode23
DEFVAR GF@counter
MOVE GF@counter string@ \# Inicializace proměnné na prázdný řetězec
\# Jednoduchá iterace ,dokud nebude splněna zadaná podmínka
LABEL while
JUMPIFEQ end GF@counter string@aaa
WRITE string@Proměnná\032GF@counter\032obsahuje\032
WRITE GF@counter
WRITE string@\010
CONCAT GF@counter GF@counter string@a
JUMP while
LABEL end
