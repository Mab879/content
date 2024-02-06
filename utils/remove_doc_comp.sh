#!/bin/bash


while IFS= read -r -d '' file
do
	sed -i '/documentation_complete: true\n'/d "$file"
done < <(find products -name '*.profile' -print0)
