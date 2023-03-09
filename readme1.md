##Implementační dokumentace k 1. úloze do IPP 2023
##Jméno a příjmení: Jakub Lukáš
##Login: xlukas18

###úvod a základní funkcionalita
Skript parse.php je napsaný v jazice php8.1. Skript bere ze standartního vstupu kód v jazyce IPPcode23. Provede lexikání a syntaktickou analýzu a vytvoří podle vstupního kódu jeho xml reprezentaci, kterou dá na standartní výstup.

###Implementace
Přes pobídku řešit projekt objekově jsem se rozhodl ho implementovat funkcionálně. Skript po zpracování argumentů postupně ve smyčce načítá řádky vstupního souboru. Když je na řádku komentář, odstraní ho. Prázdné řádky, nebo řádky obsahující jen bíle znaky jsou přeskočeny. Je kontrolováno, zda první neprázdný řádek je korektně zapsaná hlavička vstupního programu, když ano, překlad pokračuje. Jedná-li se o řádek s funkčním kódem je podle bílích znaků řádek rozdělen pomocí funkce preg_split do prvků pole. Podle operačního kódu instrukce je na jsou na její parametry volány funkce pro syntaktickou kontrolu proměných (check_var, check_sym, check_label, check_type). Funkce pro kontrolu argumentů fungují na bázi regulárního výrazu. Když jsou argumetny korektně zapsány, je zavolána funkce pro výpis xlm reprezentace instrukce print_instruction. Ta využívá php knihovnu simple XML. Po kontrole celého vstupního souboru je vypsána na standartní výstup xml reprezentace vstupního kódu. Při jakékoliv lexikální nebo syntaktické chybě je vypsána chybová hláška na standartní chybový výstup a skript ukončen s příslušnou návratovou hodnotou.
