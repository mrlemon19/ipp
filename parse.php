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

// input handle
if ($argc != 2) {
    echo "Chyba: Nespravny pocet argumentu.\n";
    exit(10);
}

if ($argv[1] == "--help") {
    // TODO official help message
    echo "Skript pro parsovani IPPcode23 zdrojaku do XML reprezentace.\n";
    exit(0);
}

$source = fopen($argv[1], "r") or exit (11); // TODO: error message
$headerok = false;

while ($line = fgets($source)) {
    
    // comment remooval
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
        echo "header: ".$headersplit[0]."\n";
        echo "count(\$headersplit): ".count($headersplit)."\n";
        echo "strcasecmp(): ".strcasecmp($headersplit[0], ".ippcode23")."\n";
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
        echo "MOVE\n";
    }
    else if (strcasecmp($linesplit[0], "createframe") == 0){
        count_args($linesplit, 1);
        echo "CREATEFRAME\n";
    }
    else if (strcasecmp($linesplit[0], "pushframe") == 0){
        count_args($linesplit, 1);
        echo "PUSHFRAME\n";
    }
    else if (strcasecmp($linesplit[0], "popframe") == 0){
        count_args($linesplit, 1);
        echo "POPFRAME\n";
    }
    else if (strcasecmp($linesplit[0], "defvar") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        echo "DEFVAR\n";
    }
    else if (strcasecmp($linesplit[0], "call") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "CALL\n";
    }
    else if (strcasecmp($linesplit[0], "return") == 0){
        count_args($linesplit, 1);
        echo "RETURN\n";
    }
    else if (strcasecmp($linesplit[0], "pushs") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "PUSHS\n";
    }
    else if (strcasecmp($linesplit[0], "pops") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        echo "POPS\n";
    }
    else if (strcasecmp($linesplit[0], "add") == 0){
        check_3argsinst($linesplit);
        echo "ADD\n";
    }
    else if (strcasecmp($linesplit[0], "sub") == 0){
        check_3argsinst($linesplit);
        echo "SUB\n";
    }
    else if (strcasecmp($linesplit[0], "mul") == 0){
        check_3argsinst($linesplit);
        echo "MUL\n";
    }
    else if (strcasecmp($linesplit[0], "idiv") == 0){
        check_3argsinst($linesplit);
        echo "IDIV\n";
    }
    else if (strcasecmp($linesplit[0], "lt") == 0){
        check_3argsinst($linesplit);
        echo "LT\n";
    }
    else if (strcasecmp($linesplit[0], "gt") == 0){
        check_3argsinst($linesplit);
        echo "GT\n";
    }
    else if (strcasecmp($linesplit[0], "eq") == 0){
        check_3argsinst($linesplit);
        echo "EQ\n";
    }
    else if (strcasecmp($linesplit[0], "and") == 0){
        check_3argsinst($linesplit);
        echo "AND\n";
    }
    else if (strcasecmp($linesplit[0], "or") == 0){
        check_3argsinst($linesplit);
        echo "OR\n";
    }
    else if (strcasecmp($linesplit[0], "not") == 0){
        check_3argsinst($linesplit);
        echo "NOT\n";
    }
    else if (strcasecmp($linesplit[0], "int2char") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "INT2CHAR\n";
    }
    else if (strcasecmp($linesplit[0], "stri2int") == 0){
        check_3argsinst($linesplit);        
        echo "STRI2INT\n";
    }
    else if (strcasecmp($linesplit[0], "read") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_type($linesplit[2]);
        echo "READ\n";
    }
    else if (strcasecmp($linesplit[0], "write") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "WRITE\n";
    }
    else if (strcasecmp($linesplit[0], "concat") == 0){
        check_3argsinst($linesplit);
        echo "CONCAT\n";
    }
    else if (strcasecmp($linesplit[0], "strlen") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "STRLEN\n";
    }
    else if (strcasecmp($linesplit[0], "getchar") == 0){
        check_3argsinst($linesplit);
        echo "GETCHAR\n";
    }
    else if (strcasecmp($linesplit[0], "setchar") == 0){
        check_3argsinst($linesplit);
        echo "SETCHAR\n";
    }
    else if (strcasecmp($linesplit[0], "type") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "TYPE\n";
    }
    else if (strcasecmp($linesplit[0], "label") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "LABEL\n";
    }
    else if (strcasecmp($linesplit[0], "jump") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "JUMP\n";
    }
    else if (strcasecmp($linesplit[0], "jumpifeq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        echo "JUMPIFEQ\n";
    }
    else if (strcasecmp($linesplit[0], "jumpifneq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        echo "JUMPIFNEQ\n";
    }
    else if (strcasecmp($linesplit[0], "exit") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "EXIT\n";
    }
    else if (strcasecmp($linesplit[0], "dprint") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "DPRINT\n";
    }
    else if (strcasecmp($linesplit[0], "break") == 0){
        count_args($linesplit, 1);
        echo "BREAK\n";
    }
    else{
        echo "ERROR: Unknown instruction.\n";
        exit(22);
    }
}

fclose($source);
exit(0);

?>
