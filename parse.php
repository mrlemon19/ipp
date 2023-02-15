<?php
// ipp projects, xlukas18 2023

class Instruction {
    public $line;           // line number in source code
    public $opcode;         // opcode
    public $arg1;           // first argument
    public $arg2 = null;    // second argument
    public $arg3 = null;    // third argument
}

// input handle
if ($argc != 2) {
    echo "Chyba: Nespravny pocet argumentu.\n";
    exit(10);
}

if ($argv[1] == "--help") {
    echo "Skript pro parsovani IPPcode23 zdrojaku do XML reprezentace.\n";
    exit(0);
}

$source = fopen($argv[1], "r") or exit (11); // TODO: error message
$linenumber = 1;

while ($line = fgets($source)) {
    $linearr = explode(" ", $line);
    echo $linenumber." ";
    $linenumber++;
    for ($i = 0; $i < count($linearr); $i++) {
        if ($linearr[$i] == "#"){
            break;
        }
        else{
            echo $linearr[$i];
            
        }
    }
}

fclose($source);
exit(0);

?>
