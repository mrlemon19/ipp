<?php
// ipp projects, xlukas18 2023
//ini_set('display_errors', 'stderr');

// funkce pro kontrolu spravneho poctu argumentu instrukce
function count_args($args, $count){
    if (count($args) != $count){
        echo "parse.php(23): spatny pocet argumentu ".join(" ", $args).", ".$count." expected ".count($args)." got\n";
        exit(23);
    }
}

// funkce pro kontrolu syntakticke spravnosti promenne, symbolu, labelu a typu
function check_var($var){
    if (preg_match("/^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $var)){
        return;
    }
    else{
        echo "parse.php(23): chybne zapsana promena ".$var."\n";
        exit(23);
    }
}

function check_sym($sym){
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

function check_label($label){
    if (preg_match("/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $label)){
        return;
    }
    else{
        echo "parse.php(23): chybne zapsany label ".$label."\n";
        exit(23);
    }
}

function check_type($type){
    if (preg_match("/^(int|string|bool)$/", $type)){
        return;
    }
    else{
        echo "parse.php(23): neplatny typ ".$type."\n";
        exit(23);
    }
}

function check_3argsinst($args){
    count_args($args, 4);
    check_var($args[1]);
    check_sym($args[2]);
    check_sym($args[3]);
}

// funkce pro vypis xml reprezentace instrukce
function print_instruction($args, $instorder){
    
    global $instorder;

    echo " <instruction order=\"".$instorder."\" opcode=\"".strtoupper($args[0])."\">\n";
    
    for ($i = 1; $i < count($args); $i++){
        
        $argsplit = explode("@", $args[$i]);
        
        if ($argsplit[0] == "GF" || $argsplit[0] == "LF" || $argsplit[0] == "TF"){
            // promena
            echo "  <arg".($i)." type=\"var\">".$args[$i]."</arg".($i).">\n";
        }
        else{
            // symbol/label/typ
            if (count($argsplit) > 1){
                // symbol/typ
                $position = strpos($args[$i], "@");
                echo "  <arg".($i)." type=\"".$argsplit[0]."\">".substr($args[$i], $position + 1)."</arg".($i).">\n";
            }
            else{
                // label
                echo "  <arg".($i)." type=\"label\">".$args[$i]."</arg".($i).">\n";
            }
        }
    }
    
    echo " </instruction>\n";
    $instorder++;
}

// input handle
if ($argc > 1){
    if ($argv[1] == "--help") {
        // help message
        echo "parse.php\nTento skript preklada kod zapsany v IPPcode23 do XML reprezentace.\n";
        echo "Usage: php parse.php [--help] <inputfile\n";
        exit(0);
    }
    else{
        echo "parse.php(10): Nespravny argument.\n";
        exit(10);
    }
}

$headerok = false;  // hlavicka je validni
$instorder = 1;     // poradi instrukce

while ($line = fgets(STDIN)) {
    
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
            echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
            echo "<program language=\"IPPcode23\">\n";
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

    if (strcasecmp($linesplit[0], "move") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "createframe") == 0){
        count_args($linesplit, 1);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "pushframe") == 0){
        count_args($linesplit, 1);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "popframe") == 0){
        count_args($linesplit, 1);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "defvar") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "call") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "return") == 0){
        count_args($linesplit, 1);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "pushs") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "pops") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "add") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "sub") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "mul") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "idiv") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "lt") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "gt") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "eq") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "and") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "or") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "not") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "int2char") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "stri2int") == 0){
        check_3argsinst($linesplit);        
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "read") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_type($linesplit[2]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "write") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "concat") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "strlen") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "getchar") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "setchar") == 0){
        check_3argsinst($linesplit);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "type") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "label") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "jump") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "jumpifeq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "jumpifneq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "exit") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "dprint") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        print_instruction($linesplit, $instorder);
    }
    else if (strcasecmp($linesplit[0], "break") == 0){
        count_args($linesplit, 1);
        print_instruction($linesplit, $instorder);
    }
    else{
        echo "ERROR: Unknown instruction.\n";
        exit(22);
    }
}

echo "</program>\n";

exit(0);

?>
