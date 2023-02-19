<?php
// ipp projects, xlukas18 2023
//ini_set('display_errors', 'stderr');

function count_args($args, $count){
    if (count($args) != $count){
        echo "Chyba: Nespravny pocet argumentu.\n";
        exit(23);
    }
}

// functions to check syntax of instruction arguments
function check_var($var){
    if (preg_match("/^(GF|LF|TF)@([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $var)){
        return;
    }
    else{
        echo "Chyba: Neplatna promenna.\n";
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
        echo "Chyba: Neplatny symbol.\n";
        exit(23);
    }
}

function check_label($label){
    if (preg_match("/^([a-zA-Z]|_|-|\$|&|%|\*|!|\?)([a-zA-Z]|_|-|\$|&|%|\*|!|\?|\d)*$/", $label)){
        return;
    }
    else{
        echo "Chyba: Neplatny label.\n";
        exit(23);
    }
}

function check_type($type){
    if (preg_match("/^(int|string|bool)$/", $type)){
        return;
    }
    else{
        echo "Chyba: Neplatny typ.\n";
        exit(23);
    }
}

function check_3argsinst($args){
    count_args($args, 4);
    check_var($args[1]);
    check_sym($args[2]);
    check_sym($args[3]);
}

function print_instruction($args, $instorder){
    global $instorder;
    
    if ($instorder == 1){
        echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        echo "<program language=\"IPPcode23\">\n";
    }

    echo "\t<instruction order=\"".$instorder."\" opcode=\"".strtoupper($args[0])."\">\n";
    
    for ($i = 1; $i < count($args); $i++){
        $argsplit = explode("@", $args[$i]);
        
        if ($argsplit[0] == "GF" || $argsplit[0] == "LF" || $argsplit[0] == "TF"){
            echo "\t\t<arg".($i)." type=\"var\">".$args[$i]."</arg".($i).">\n";
        }
        else{
            $position = strpos($args[$i], "@");
            echo "\t\t<arg".($i)." type=\"".$argsplit[0]."\">".substr($args[$i], $position + 1)."</arg".($i).">\n";
        }
    }
    
    echo "\t</instruction>\n";
    $instorder++;
}

 input handle
if ($argc != 2) {
    echo "Chyba: Nespravny pocet argumentu.\n";
    exit(10);
}

if ($argv[1] == "--help") {
    // TODO official help message
    echo "Skript pro parsovani IPPcode23 zdrojaku do XML reprezentace.\n";
    exit(0);
}

$headerok = false;  // true if header is valid
$instorder = 1;     // instruction order

while ($line = fgets(STDIN)) {
    
    // comment removal
    if (($pos = strpos($line, "#")) !== false) {
        if ($pos == 0)
            continue;
        else
            $line = substr($line, 0, $pos);
    }

    // checking header
    if (!$headerok){
        $line = trim($line);
        $headersplit = preg_split('/\s+/', $line);
        // *debug*
        //echo "header: ".$headersplit[0]."\n";
        //echo "count(\$headersplit): ".count($headersplit)."\n";
        //echo "strcasecmp(): ".strcasecmp($headersplit[0], ".ippcode23")."\n";
        if (count($headersplit) == 1 && strcasecmp($headersplit[0], ".ippcode23") == 0){
            $headerok = true;
            continue;
        }
        else{
            echo "Chyba hlavicky\n";
            exit(21);
        }
    }

    // skips empty line
    if ($line == "\n"){
        continue;
    }

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
