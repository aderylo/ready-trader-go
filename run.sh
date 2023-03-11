#!/bin/bash

# build 
cmake -DCMAKE_BUILD_TYPE=Release -B build
cmake --build build --config Release

# copy
cp build/autotrader .

# run
nohup python3 rtg.py run autotrader &