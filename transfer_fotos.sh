#!/bin/bash
# Distribute fotos in .tmp into their according directoy.
# After this step, the entry will be assembled. A txt-file with a discription should already be there.

for f in .tmp/*; do
	date_created=$(exif -t 0x9003 --ifd=EXIF "$f" | tail -1 | cut -d' ' -f4 | awk -F: '{print $3"."$2"."$1}')
	day=$(cut -d '.' -f1 <(echo "$date_created"))
	month=$(cut -d '.' -f2 <(echo "$date_created"))
	year=$(cut -d '.' -f3 <(echo "$date_created"))

	# Find all directories obeying the scheme
	# There should only be 1 but checking beforehand might be a good option.
	matching_dirs=("$year/$month-"*/"$day-"*)
	count=${#matching_dirs[@]}
	if [ $count -gt 1 ]; then
	  notify-send "Found $count matching directories obeying '$year/$month-*/$day-*'. There should be exactly 1."
	  exit 1
	else
		# Transfer image to directory
		for d in "${matching_dirs[@]}"; do
			cp "$f" "$d/$(basename "$f")"
		done
	fi
done
