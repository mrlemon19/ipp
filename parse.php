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
    
    if ($instorder == 1){
        echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
        echo "<program language=\"IPPcode23\">\n";
    }

    echo "\t<instruction order=\"".$instorder."\" opcode=\"".strtoupper($args[0])."\">\n";
    $args = array_slice($args, 1);
    
    for ($i = 0; $i < count($args); $i++){
        $argsplit = explode("@", $args[$i]);
        
        if ($argsplit[0] == "GF" || $argsplit[0] == "LF" || $argsplit[0] == "TF")
            echo "\t\t<arg".($i+1)." type=\"var\">".$args[$i]."</arg".($i+1).">\n";
        else{
            $position = strpos($args[$i], "@");
            echo "\t\t<arg".($i+1)." type=\"".$argsplit[0]."\">".substr($args[$i], $position + 1)."</arg".($i+1).">\n";
        }
        echo "\t\t<arg".($i+1)." type=\"".gettype($args[$i])."\">".$args[$i]."</arg".($i+1).">\n";
    }
    
    echo "\t</instruction>";
}

// input handle
//if ($argc != 2) {
//    echo "Chyba: Nespravny pocet argumentu.\n";
//    exit(10);
//}

//if ($argv[1] == "--help") {
//    // TODO official help message
//    echo "Skript pro parsovani IPPcode23 zdrojaku do XML reprezentace.\n";
//    exit(0);
//}

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
        echo "MOVE\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "createframe") == 0){
        count_args($linesplit, 1);
        echo "CREATEFRAME\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "pushframe") == 0){
        count_args($linesplit, 1);
        echo "PUSHFRAME\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "popframe") == 0){
        count_args($linesplit, 1);
        echo "POPFRAME\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "defvar") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        echo "DEFVAR\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "call") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "CALL\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "return") == 0){
        count_args($linesplit, 1);
        echo "RETURN\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "pushs") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "PUSHS\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "pops") == 0){
        count_args($linesplit, 2);
        check_var($linesplit[1]);
        echo "POPS\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "add") == 0){
        check_3argsinst($linesplit);
        echo "ADD\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "sub") == 0){
        check_3argsinst($linesplit);
        echo "SUB\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "mul") == 0){
        check_3argsinst($linesplit);
        echo "MUL\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "idiv") == 0){
        check_3argsinst($linesplit);
        echo "IDIV\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "lt") == 0){
        check_3argsinst($linesplit);
        echo "LT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "gt") == 0){
        check_3argsinst($linesplit);
        echo "GT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "eq") == 0){
        check_3argsinst($linesplit);
        echo "EQ\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "and") == 0){
        check_3argsinst($linesplit);
        echo "AND\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "or") == 0){
        check_3argsinst($linesplit);
        echo "OR\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "not") == 0){
        check_3argsinst($linesplit);
        echo "NOT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "int2char") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "INT2CHAR\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "stri2int") == 0){
        check_3argsinst($linesplit);        
        echo "STRI2INT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "read") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_type($linesplit[2]);
        echo "READ\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "write") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "WRITE\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "concat") == 0){
        check_3argsinst($linesplit);
        echo "CONCAT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "strlen") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "STRLEN\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "getchar") == 0){
        check_3argsinst($linesplit);
        echo "GETCHAR\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "setchar") == 0){
        check_3argsinst($linesplit);
        echo "SETCHAR\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "type") == 0){
        count_args($linesplit, 3);
        check_var($linesplit[1]);
        check_sym($linesplit[2]);
        echo "TYPE\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "label") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "LABEL\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "jump") == 0){
        count_args($linesplit, 2);
        check_label($linesplit[1]);
        echo "JUMP\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "jumpifeq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        echo "JUMPIFEQ\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "jumpifneq") == 0){
        count_args($linesplit, 4);
        check_label($linesplit[1]);
        check_sym($linesplit[2]);
        check_sym($linesplit[3]);
        echo "JUMPIFNEQ\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "exit") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "EXIT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "dprint") == 0){
        count_args($linesplit, 2);
        check_sym($linesplit[1]);
        echo "DPRINT\n";
        $instorder++;
    }
    else if (strcasecmp($linesplit[0], "break") == 0){
        count_args($linesplit, 1);
        echo "BREAK\n";
        $instorder++;
    }
    else{
        echo "ERROR: Unknown instruction.\n";
        exit(22);
    }
}

echo "</program>";

exit(0);

?>
