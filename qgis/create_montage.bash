#!/usr/bin/env bash

set -euo pipefail

output_dir=/mnt/c/tmp
output="${output_dir}/montage.jpg"
secondary_output=../outputs/final/source_montage.jpg

# Test if output_dir exists
# if not, use secondary_output as main
[[ -d "$output_dir" ]] || output="$secondary_output"

    # \( outputs/map_mag_2.jpg -draw "text 40,270 'D.'" \) \
    # -pointsize 250 \
    # \( outputs/map_mag_3.jpg -draw "text 40,270 'E.'" \) \
    # -pointsize 250 \

magick montage -background 'black' \
    -font Liberation-Mono-Bold \
    -pointsize 250 \
    \( outputs/map_dem.jpg -draw "text 40,270 '(a)'"  \) \
    -pointsize 250 \
    \( outputs/map_em.jpg -draw "text 40,270 '(b)'" \) \
    -pointsize 250 \
    \( outputs/map_mag_1.jpg -draw "text 40,270 '(c)'" \) \
    -pointsize 250 \
    \( outputs/map_int.jpg -draw "text 40,270 '(d)'" \) \
    -mattecolor "black" \
    -fill "black" \
    -stroke "white" \
    -bordercolor "black" \
    -geometry 1100x \
    -tile 2x2 \
    -border 2 \
    -frame 2 \
    "$output"

# If output is different from secondary_output, copy main to secondary
[[ "$output" = "$secondary_output" ]] || cp "$output" "$secondary_output"
