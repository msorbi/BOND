#!/bin/bash
if [ $# -ne 1 ] || ([ "$1" != "supervised" ] && [ "$1" != "distant" ])
then
    echo "usage: $0 (supervised|distant)"
    exit 1
fi
setting="$1"

source="hdsner-utils/data/${setting}/ner_medieval_multilingual/FR/"
output_dir="dataset"
dataset_prefix="hdsner-"
dataset_suffix="_${setting}"

# copy and format datasets
python3 scripts/format_hdsner_datasets.py \
    --input-dir "${source}" \
    --output-dir "${output_dir}" \
    "--output-prefix=${dataset_prefix}" \
    "--output-suffix=${dataset_suffix}"

# execute on all datasets
for dataset in ${output_dir}/${dataset_prefix}*${dataset_suffix}
do
    dataset_name="`basename ${dataset}`"
    time \
    bash scripts/hdsner_training.sh 0 "${dataset_name}" \
    > "${dataset}/stdout.txt" 2> "${dataset}/stderr.txt"
done
