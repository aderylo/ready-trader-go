#!/bin/bash

# Get the folder path from the command line argument
folder="$1"

# Use the find command to locate all .log files in subdirectories of the given folder
# and pass them to the rm command to delete them
find "$folder" -type f -name "*.log" -delete
find "$folder" -type f -name "*.dat" -delete
find "$folder" -type f -name "*.csv" -delete