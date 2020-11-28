#!/bin/bash

### VARIABLES ###

PROGNAME="$(basename "$0")"
INPUT_SOURCE=$1
QUALITY_HD=23
QUALITY_4K=22
FILEDIR=$(dirname "$INPUT_SOURCE")


### FUNCTIONS###

### Function: Help

Help()
{
   echo "This script uses sensible ffmpeg options to batch encode MKV files in a directory to compressed H264 MKVs."
   echo "You can change the CRF parameters in the script, defaults are 24 for HD and 22 for 4K."
   echo
   echo "SYNTAX: ./ffmpeg-encode.sh 'INPUT DIRECTORY'"
   echo "EXAMPLE: ./ffmpeg-encode.sh ~/Videos/Movies"
   echo
   echo "Learn more about FFmpeg's quality settings: https://trac.ffmpeg.org/wiki/Encode/H.264"
}

### Funtion: Error

error_exit()
{
  echo "${PROGNAME}: ${1:-"Unknown Error"}" 1>&2
  exit 1
}


# Function: encode each file in the directory with different CRF setting based on resolution

folder_encode () {
    if [ ! -d "$INPUT_SOURCE/output" ]; then
    mkdir "$INPUT_SOURCE/output"
    fi

    for FILE in "$INPUT_SOURCE"/*.*; do
        RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$FILE")
        FILENAME=$(basename "$FILE")
            if [[ $RES -gt 1920 ]]; then
                echo "File is 4K or higher, encoding using CRF $QUALITY_4K"
                ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_4K" -c:a copy "$INPUT_SOURCE"/output/"$FILENAME" ||  echo "ERROR Line $LINENO: File not encoded, unknown error occurred." 1>&2
            elif [[ $RES -le 1920 ]] && [[ -n $RES ]]; then
                echo "File is HD or lower, encoding using CRF $QUALITY_HD"
                ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_HD" -c:a copy "$INPUT_SOURCE"/output/"$FILENAME" ||  echo "ERROR Line $LINENO: File not encoded, unknown error occurred." 1>&2
            else
                echo "ERROR Line $LINENO: Source file $FILE is not a valid video file" 1>&2
                echo "Skipping..."
            fi
    done
}

# Function: encode single file with different CRF setting based on resolution

file_encode () {
    if [ ! -d "$FILEDIR/output" ]; then
    mkdir "$FILEDIR/output"
    fi

    FILENAME=$(basename "$INPUT_SOURCE")
    RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$INPUT_SOURCE")
        if [[ $RES -gt 1920 ]]; then
            echo "File is 4K or higher, encoding using CRF $QUALITY_4K"
            ffmpeg -i "$INPUT_SOURCE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_4K" -c:a copy "$FILEDIR"/output/"$FILENAME" || echo "ERROR Line $LINENO: File not encoded, unknown error occurred." 1>&2
        elif [[ $RES -le 1920 ]] && [[ -n $RES ]]; then
            echo "File is HD or lower, encoding using CRF $QUALITY_HD"
            ffmpeg -i "$INPUT_SOURCE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_HD" -c:a copy "$FILEDIR"/output/"$FILENAME" || echo "ERROR Line $LINENO: File not encoded, unknown error occurred." 1>&2
        else
            echo "ERROR Line $LINENO: Source file $INPUT_SOURCE is not a valid video file" 1>&2
        fi
}

### SCRIPT ###

# Check if source input is provided
if [ -z "$1" ]; then
    printf "ERROR: You must specify a source directory\n\n" 1>&2
    Help
    exit 1
fi

# Run function based on file or folder input
if [ -f "$1" ]; then
    file_encode || error_exit "$LINENO: An error has occurred." 1>&2
elif [ -d "$1" ]; then
    folder_encode || error_exit "$LINENO: An error has occurred." 1>&2
else
    error_exit "$LINENO: Not a valid source" 1>&2
fi

<<<<<<< HEAD
echo "File(s) encoded successfully!"

exit 0

=======
# Encode each file in the directory with different CRF setting based on resolution
for FILE in "$DIRECTORY"/*.*; do
    RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=noprint_wrappers=1:nokey=1 "$FILE")
    FILENAME=$(basename "$FILE")
        if [[ $RES -gt 1920 ]]; then
            ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_4K" -c:a copy "$DIRECTORY"/output/"$FILENAME"
        elif [[ $RES -le 1920 ]]; then
            ffmpeg -i "$FILE" -c:v libx264 -preset slow -tune film -crf "$QUALITY_HD" -c:a copy "$DIRECTORY"/output/"$FILENAME"
        else
            echo "$FILENAME is not a valid filetype"
        fi
done
>>>>>>> main

