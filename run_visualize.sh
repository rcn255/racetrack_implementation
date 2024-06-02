#!/bin/bash

# Check if the correct number of arguments is provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <trackFile> <tripFile> <outputFile>"
    exit 1
fi

# Assign positional parameters to variables
trackFile=$1
tripFile=$2
outputFile=$3

# Call the Perl script with the provided arguments
perl visualise.pl "$trackFile" "$tripFile" "$outputFile"
pdflatex "$outputFile"

tripFileName=$(basename "$tripFile" .rl)

outputDirectory="latex_trips/$tripFileName"

# Create the directory if it doesn't exist
mkdir -p "$outputDirectory"

# Move the generated files into the created directory
mv "${tripFileName}."* "$outputDirectory/"