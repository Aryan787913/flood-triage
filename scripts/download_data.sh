#!/usr/bin/env bash
# Downloads STURM-FloodDepth Flooded Cars (Notarangelo, 2025; CC BY 4.0; doi:10.5281/zenodo.14833532).
# Images are NOT redistributed in this repo.
set -euo pipefail
mkdir -p data splits
cd data
if [ ! -f flooded_cars.zip ]; then curl -L -o flooded_cars.zip "https://zenodo.org/records/14833532/files/flooded_cars.zip?download=1"; fi
echo "d1e4de73145e807dd691718aea136508  flooded_cars.zip" | md5sum -c -
unzip -qn flooded_cars.zip
cd ../splits
for s in train val test; do curl -sL -o $s.txt "https://zenodo.org/records/14833532/files/$s.txt?download=1"; done
cd ..; echo "OK: $(find data/upscaled_images -name '*.jpg' | wc -l) images"
