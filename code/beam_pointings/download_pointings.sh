#!/bin/bash

for i in {1..56}
do
    wget "http://ws.mwatelescope.org/metadata/find?mintime=1252195218&maxtime=1255219218&extended=1&page=$i" -O pointings_$i.txt
    sleep 49
done    


