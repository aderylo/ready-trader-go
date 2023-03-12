
#!/bin/bash

readonly test_name="$1"

cp build/autotrader tests/configs/$test_name 
# cp tests/configs/$test_name/exchange.json exchange.json