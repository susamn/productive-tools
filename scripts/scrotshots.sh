#!/bin/bash

# Base directory to save screenshots
base_dir="$HOME/Pictures/Screenshots"

# Date-based directory
date_dir=$(date +'%b%d-%Y')

# Full directory path
screenshot_dir="$base_dir/$date_dir"

# Create directory if it doesn't exist
mkdir -p "$screenshot_dir"

# Base filename without the date part
base_filename="SUSAMN-$(date +'%Y-%b%d')"

# Function to determine the next filename
get_next_filename() {
    last_file=$(ls -t "$screenshot_dir" | grep "^$base_filename" | head -n 1)
    if [[ -z "$last_file" ]]; then
        # No files exist, start with 1a
        echo "$base_filename-1a.png"
    else
        # Extract the counter and suffix from the last file
        last_counter_suffix=$(echo "$last_file" | sed -r "s/$base_filename-([0-9]+[a-z])\.png/\1/")
        last_counter=${last_counter_suffix%?}
        last_suffix=${last_counter_suffix: -1}

        if [[ "$last_suffix" == "a" ]]; then
            # If the last suffix is 'a', increment to 'b'
            next_suffix="b"
            next_counter="$last_counter"
        else
            # If the last suffix is 'b', increment the counter and set suffix to 'a'
            next_suffix="a"
            next_counter=$((last_counter + 1))
        fi
        echo "$base_filename-$next_counter$next_suffix.png"
    fi
}

# Get the next filename
filename=$(get_next_filename)

# Take the screenshot with selection window
scrot -s "$screenshot_dir/$filename"

echo "Screenshot saved as $filename in $screenshot_dir"
