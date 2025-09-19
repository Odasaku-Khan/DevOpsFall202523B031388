#!/bin/bash

my_id="23B031388"
current_zip="archive_1.zip"
while [[ -f "$current_zip" ]]; do
    echo "Processing $current_zip ..."
    temp_dir=$(mktemp -d)
    unzip -o "$current_zip" -d "$temp_dir" >/dev/null
    code_file=$(grep -ril "CodeWord" "$temp_dir" | head -n 1)
    if [[ -n "$code_file" ]]; then
        old_code=$(grep -o "CodeWord_[0-9A-Z]\+" "$code_file")
        new_code="${old_code}_${my_id}"
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/${old_code}/${new_code}/g" "$code_file"
        else
            sed -i "s/${old_code}/${new_code}/g" "$code_file"
        fi
        echo "Code replaced: $old_code -> $new_code"
        (cd "$temp_dir" && zip -r "../${current_zip%.zip}_modified.zip" ./* >/dev/null)
        echo "Modified archive created: ${current_zip%.zip}_modified.zip"
        rm -rf "$temp_dir"
        break
    fi
    nested_zip_path=$(find "$temp_dir" -type f -name "*.zip" | head -n 1)
    if [[ -n "$nested_zip_path" ]]; then
        current_zip="$nested_zip_path"
    else
        echo "No more nested ZIPs found. Stopping."
        rm -rf "$temp_dir"
        break
    fi
done
echo "Script finished."