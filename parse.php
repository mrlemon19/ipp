<?php
// ipp projects, xlukas18 2023

class Instruction {
    public $line;           // line number in source code
    public $opcode;         // opcode
    public $arg1;           // first argument
    public $arg2;           // second argument
    public $arg3;           // third argument

    function __construct($line, $opcode, $arg1, $arg2=null, $arg3=null) {
        $this->line = $line;
        $this->opcode = $opcode;
        $this->arg1 = $arg1;
        $this->arg2 = $arg2;
        $this->arg3 = $arg3;
    }
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
$instarray = array();

while ($line = fgets($source)) {
    $linearr = explode(" ", $line);
    echo $linenumber." ";
    $linenumber++;

    rtrim($linearr[count($linearr)-1], "\n");
    for ($i = 0; $i < count($linearr); $i++) {

        if ($linearr[$i] == "#" or $linearr[$i] == "\n"){
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
