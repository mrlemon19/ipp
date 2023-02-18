<?php
// ipp projects, xlukas18 2023
//ini_set('display_errors', 'stderr');

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

while ($line = fgets($source)) {

    if ($line == "\n" || $line == ".IPPcode23\n"){
        continue;
    }

    // TODO propper header check
    
    // comment remooval
    if (($pos = strpos($line, "#")) !== false) {
        if ($pos == 0)
            continue;
        else
            $line = substr($line, 0, $pos);
    }

    $linesplit = explode(" ", $line);
    $linesplit[count($linesplit)-1] = rtrim($linesplit[count($linesplit)-1], "\n");
    
    switch($linesplit[0]){
        case "MOVE":
            echo "MOVE";
            break;
        case "CREATEFRAME":
            echo "CREATEFRAME";
            break;
        case "PUSHFRAME":
            echo "PUSHFRAME";
            break;
        case "POPFRAME":
            echo "POPFRAME";
            break;
        case "DEFVAR":
            echo "DEFVAR";
            break;
        case "CALL":
            echo "CALL";
            break;
        case "RETURN":
            echo "RETURN";
            break;
        case "PUSHS":
            echo "PUSHS";
            break;
        case "POPS":
            echo "POPS";
            break;
        case "ADD":
            echo "ADD";
            break;
        case "SUB":
            echo "SUB";
            break;
        case "MUL":
            echo "MUL";
            break;
        case "IDIV":
            echo "IDIV";
            break;
        case "LT":
            echo "LT";
            break;
        case "GT":
            echo "GT";
            break;
        case "EQ":
            echo "EQ";
            break;
        case "AND":
            echo "AND";
            break;
        case "OR":
            echo "OR";
            break;
        case "NOT":
            echo "NOT";
            break;
        case "INT2CHAR":
            echo "INT2CHAR";
            break;
        case "STRI2INT":
            echo "STRI2INT";
            break;
        case "READ":
            echo "READ";
            break;
        case "WRITE":
            echo "WRITE";
            break;
        case "CONCAT":
            echo "CONCAT";
            break;
        case "STRLEN":
            echo "STRLEN";
            break;
        case "GETCHAR":
            echo "GETCHAR";
            break;
        case "SETCHAR":
            echo "SETCHAR";
            break;
        case "TYPE":
            echo "TYPE";
            break;
        case "LABEL":
            echo "LABEL";
            break;
        case "JUMP":
            echo "JUMP";
            break;
        case "JUMPIFEQ":
            echo "JUMPIFEQ";
            break;
        case "JUMPIFNEQ":
            echo "JUMPIFNEQ";
            break;
        case "EXIT":
            echo "EXIT";
            break;
        case "DPRINT":
            echo "DPRINT";
            break;
        case "BREAK":    
            echo "BREAK";
            break;
        default:
            echo "Chyba: Neznamy instrukcni kod.\n";
            echo $linesplit[0]."\n";
            exit(22);

    }

    //for ($i = 0; $i < count($linesplit); $i++) {
    //
    //    if ($linesplit[$i] == "#"){
    //        break;
    //    }
    //    else{
    //        echo $linesplit[$i];
    //        
    //    }
    //}
}

fclose($source);
exit(0);

?>
