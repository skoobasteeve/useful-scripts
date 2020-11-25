#!/bin/bash

### Help function ###

Help()
{
   # Display Help
   echo "This script uses sensible ffmpeg options to batch encode MKV files in a directory to compressed H264 MKVs."
   echo "You can change the CRF parameters in the script, defaults are 24 for HD and 22 for 4K."
   echo
   echo "SYNTAX: ./ffmpeg-encode.sh 'INPUT DIRECTORY'"
   echo "EXAMPLE: ./ffmpeg-encode.sh ~/Videos/Movies"
   echo
   echo "Learn more about FFmpeg's quality settings: https://trac.ffmpeg.org/wiki/Encode/H.264"
}

### Error function ###

PROGNAME="$(basename $0)"

error_exit()
{

# ----------------------------------------------------------------
# Function for exit due to fatal program error
#   Accepts 1 argument:
#     string containing descriptive error message
# ----------------------------------------------------------------


  echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
  exit 1
}

# Example call of the error_exit function.  Note the inclusion
# of the LINENO environment variable.  It contains the current
# line number.

### Script ###

DIRECTORY=$1
QUALITY_HD=23
QUALITY_4K=22

# Check if source directory is provided
if [ -z "$1" ] || [ ! -d "$1" ]; then
    printf "ERROR: You must specify a source directory\n\n" 1>&2
    Help
    exit 1
fi

# Create output folder within source directory
if [ ! -d "$DIRECTORY/output" ]; then
    mkdir "$DIRECTORY/output"
fi


# Encode each file in the directory with different CRF setting based on resolution
for FILE in "$DIRECTORY"/*.*; do
    RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$FILE")
    FILENAME=$(basename "$FILE")
        if [[ $RES -gt 1920 ]]; then
            ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_4K" -c:a copy "$DIRECTORY"/output/"$FILENAME"
        elif [[ $RES -le 1920 ]]; then
            ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_HD" -c:a copy "$DIRECTORY"/output/"$FILENAME"
        fi
done || error_exit "$LINENO: An error has occurred."

exit 0