<?php
// ipp 2023 project: parse.php, @author: Jakub Lukas, xlukas18
ini_set('display_errors', 'stderr');

// kontrola spravneho poctu argumentu instrukce
function count_args($args, $count)
{
    if (count($args) != $count){
        echo "parse.php(23): spatny pocet argumentu: ".join(" ", $args).", ".$count." expected ".count($args)." got\n";
        exit(23);
    }
}

// kontrola syntakticke spravnosti promenne, symbolu, labelu a typu
function check_var($var)
{
    if (preg_match("/^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $var)){
        return;
    }
    else{
        echo "parse.php(23): chybne zapsana promena ".$var."\n";
        exit(23);
    }
}

function check_sym($sym)
{
    if (preg_match("/^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $sym)){
        return;
    }
    else if (preg_match("/^int@([+-]?[0-9]+)$/", $sym)){
        return;
    }
    else if (preg_match("/^bool@(true|false)$/", $sym)){
        return;
    }
    else if (preg_match("/^string@([^\s#\\\\]|\\\\[0-9]{3})*$/", $sym)){
        return;
    }
    else if (preg_match("/^nil@nil$/", $sym)){
        return;
    }
    else{
        echo "parse.php(23): chybne zapsany symbol ".$sym."\n";
        exit(23);
    }
}

function check_label($label)
{
    if (preg_match("/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $label)){
        return;
    }
    else{
        echo "parse.php(23): chybne zapsany label ".$label."\n";
        exit(23);
    }
}

function check_type($type)
{
    if (preg_match("/^(int|string|bool)$/", $type)){
        return;
    }
    else{
        echo "parse.php(23): neplatny typ ".$type."\n";
        exit(23);
    }
}

// vypis xml reprezentace instrukce
function print_instruction($args, $instorder)
{
    global $instorder;
    global $output;

    $instruction = $output->addChild("instruction");
    $instruction->addAttribute("order", $instorder);
    $instruction->addAttribute("opcode", $args[0]);

    for ($i = 1; $i < count($args); $i++){
        
        // prepsani problematickych znaku do xlm varianty
        $args[$i] = str_replace("&", "&amp;", $args[$i]);
        $args[$i] = str_replace("<", "&lt;", $args[$i]);
        $args[$i] = str_replace(">", "&gt;", $args[$i]);

        $argsplit = explode("@", $args[$i]);
        
        if ($argsplit[0] == "GF" || $argsplit[0] == "LF" || $argsplit[0] == "TF"){
            // promena
            $arg = $instruction->addChild("arg".($i), $args[$i]);
            $arg->addAttribute("type", "var");
        }
        else{
            // symbol/label/typ
            if (count($argsplit) > 1){
                // symbol/typ
                $position = strpos($args[$i], "@");
                $arg = $instruction->addChild("arg".($i), substr($args[$i], $position + 1));
                $arg->addAttribute("type", $argsplit[0]);
            }
            else{
                // label/typ
                if ($args[$i] == "int" || $args[$i] == "string" || $args[$i] == "bool"){
                    $arg = $instruction->addChild("arg".($i), $args[$i]);
                    $arg->addAttribute("type", "type");
                }
                else{
                    $arg = $instruction->addChild("arg".($i), $args[$i]);
                    $arg->addAttribute("type", "label");
                }
            }
        }
    }
    $instorder++;

}

// input handle
if ($argc > 1){
    if ($argv[1] == "--help") {
        // help message
        echo "parse.php\nTento skript parsuje kod zapsany v IPPcode23 do XML reprezentace.\n";
        echo "Usage: php parse.php [--help] <inputfile\n";
        exit(0);
    }
    else{
        echo "parse.php(10): Nespravny argument.\n";
        exit(10);
    }
}

if ($argc > 2){
    echo "parse.php(10): Nespravny pocet argumentu.\n";
    exit(10);
}

// xml
$output = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><program language="IPPcode23"></program>');

$headerok = false;  // hlavicka je validni kdyz true
$instorder = 1;     // poradi instrukce v kodu

while ($line = fgets(STDIN)) {
    
    // parsovani radku
    // preskoceni komentare
    if (($pos = strpos($line, "#")) !== false) {
        if ($pos == 0)
            continue;
        else
            $line = substr($line, 0, $pos);
    }

    // preskoceni prazdneho radku
    if ($line == "\n"){
        continue;
    }

    // kontrola hlavicky
    if (!$headerok){
        $line = trim($line);
        $headersplit = preg_split('/\s+/', $line);
        
        if (count($headersplit) == 1 && strcasecmp($headersplit[0], ".ippcode23") == 0){
            $headerok = true;
            continue;
        }
        else{
            echo "parse.php(21): chybne zapsana hlavicka\n";
            exit(21);
        }
    }

    // odstraneni mezer a tabulatoru
    $line = trim($line);
    $linesplit = preg_split('/\s+/', $line);
    $linesplit[count($linesplit)-1] = rtrim($linesplit[count($linesplit)-1], "\n");
    $linesplit[0] = strtoupper($linesplit[0]);

    switch ($linesplit[0]){
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
                count_args($linesplit, 1);
                print_instruction($linesplit, $instorder);
                break;
        
        case "DEFVAR":
        case "POPS":
                count_args($linesplit, 2);
                check_var($linesplit[1]);
                print_instruction($linesplit, $instorder);
                break;

        case "CALL":
        case "LABEL":
        case "JUMP":
            count_args($linesplit, 2);
            check_label($linesplit[1]);
            print_instruction($linesplit, $instorder);
            break;

        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            count_args($linesplit, 2);
            check_sym($linesplit[1]);
            print_instruction($linesplit, $instorder);
            break;

        case "MOVE":
            count_args($linesplit, 3);
            check_var($linesplit[1]);
            check_sym($linesplit[2]);
            print_instruction($linesplit, $instorder);
            break;

        case "NOT":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            count_args($linesplit, 3);
            check_var($linesplit[1]);
            check_sym($linesplit[2]);
            print_instruction($linesplit, $instorder);
            break;

        case "READ":
            count_args($linesplit, 3);
            check_var($linesplit[1]);
            check_type($linesplit[2]);
            print_instruction($linesplit, $instorder);
            break;

        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            count_args($linesplit, 4);
            check_label($linesplit[1]);
            check_sym($linesplit[2]);
            check_sym($linesplit[3]);
            print_instruction($linesplit, $instorder);
            break;

        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":
        case "GT":
        case "EQ":
        case "AND":
        case "OR":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            count_args($linesplit, 4);
            check_var($linesplit[1]);
            check_sym($linesplit[2]);
            check_sym($linesplit[3]);
            print_instruction($linesplit, $instorder);
            break;

        default: 
            echo "parse.php(22): neznamy kod instrukce.\n";
            exit(22);
    }
}

// echo "</program>\n";
$doc = new DOMDocument("1.0");
$doc->preserveWhiteSpace = false;
$doc->formatOutput = true;
$doc->loadXML($output->asXML());
echo $doc->saveXML();

exit(0);

?>
