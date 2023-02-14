<?php
// ipp projects, xlukas18 2023

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

while ($line = fgets($source)) {
    $linearr = explode(" ", $line);
    for ($i = 0; $i < count($linearr); $i++) {
        //echo $linearr[$i]."\n";
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
