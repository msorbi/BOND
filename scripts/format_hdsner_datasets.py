import argparse
import os
import json

def generate_tag_to_id_map(class_names):
    """
    Generates a tag-to-ID mapping dictionary.
    Ensures 'PERS' tags precede 'LOC' tags if both are present.
    """
    tag_to_id = {"O": 0}
    next_id = 1

    # Define the desired order for classes
    ordered_classes = []
    if "PERS" in class_names:
        ordered_classes.append("PERS")
    if "LOC" in class_names:
        ordered_classes.append("LOC")
    
    # Add any other classes found, sorted alphabetically
    for other_class in sorted(c for c in class_names if c not in ["PERS", "LOC"]):
        ordered_classes.append(other_class)

    for class_name in ordered_classes:
        tag_to_id[f"B-{class_name}"] = next_id
        next_id += 1
        tag_to_id[f"I-{class_name}"] = next_id
        next_id += 1
    
    return tag_to_id

def process_text_file_to_json(input_file_path, output_file_path, tag_to_id_map):
    """
    Reads a source .txt file, parses it into sequences, and converts it to JSON.
    Each sequence is a dictionary with "str_words" and "tags" (integer IDs).
    """
    output_data = []
    
    try:
        with open(input_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by '\n\n' to get individual sequences/sentences
        sequences = content.strip().split('\n\n')
        
        for sequence in sequences:
            if not sequence.strip(): # Skip empty sequences
                continue
            
            str_words = []
            tags_str = []
            
            lines = sequence.strip().split('\n')
            for line in lines:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    str_words.append(parts[0])
                    tags_str.append(parts[1])
                elif len(parts) == 1 and parts[0].strip(): # Handle cases where only word is present, assume 'O' tag
                    str_words.append(parts[0].strip())
                    tags_str.append("O") # Default to 'O' tag
                # Ignore empty lines or lines with more/less than 2 parts that aren't single-word lines
            
            # Convert string tags to integer IDs
            # Use .get() with a default of tag_to_id_map["O"] if tag is not found
            tags_int = [tag_to_id_map.get(tag, tag_to_id_map["O"]) for tag in tags_str]

            if str_words: # Only add to output if there are actual words in the sequence
                output_data.append({"str_words": str_words, "tags": tags_int})

        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            json.dump(output_data, outfile, indent=4, ensure_ascii=False)
        
    except FileNotFoundError:
        print(f"Warning: Source file not found: {input_file_path}")
    except Exception as e:
        print(f"Error processing {input_file_path}: {e}")


def transform_data_to_json_format(input_dir, output_dir, output_prefix, output_suffix):
    """
    Transforms the data from the input directory into the specified hierarchical
    JSON output structure.
    """
    # Ensure the main output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Iterate through each dataset (e.g., CBMA, CDBE, HOME)
    for dataset_name in os.listdir(input_dir):
        dataset_path = os.path.join(input_dir, dataset_name)
        if not os.path.isdir(dataset_path):
            continue # Skip non-directory items

        # Construct the output subdirectory name for the current dataset
        output_dataset_dir_name = f"{output_prefix}{dataset_name}{output_suffix}"
        output_dataset_path = os.path.join(output_dir, output_dataset_dir_name)
        os.makedirs(output_dataset_path, exist_ok=True) # Create the dataset-specific output directory

        multiclass_path = os.path.join(dataset_path, "MULTICLASS")
        if not os.path.isdir(multiclass_path):
            print(f"Warning: 'MULTICLASS' directory not found in '{dataset_path}'. Skipping dataset '{dataset_name}'.")
            continue

        # 1. Identify single classes in the current dataset
        current_dataset_single_classes = []
        for class_dir in os.listdir(dataset_path):
            if os.path.isdir(os.path.join(dataset_path, class_dir)) and class_dir != "MULTICLASS":
                current_dataset_single_classes.append(class_dir)
        
        # 2. Generate and save _tag_to_id.json
        tag_to_id_map = generate_tag_to_id_map(current_dataset_single_classes)
        tag_to_id_output_filename = "tag_to_id.json" # No prefix/suffix here, as it's inside the dataset dir
        tag_to_id_output_path = os.path.join(output_dataset_path, tag_to_id_output_filename)
        with open(tag_to_id_output_path, 'w', encoding='utf-8') as f:
            json.dump(tag_to_id_map, f, indent=4, ensure_ascii=False)

        # 3. Process train.txt, val.txt, test.txt from MULTICLASS to JSON
        file_mappings = {
            "train.txt": "train.json",
            "val.txt": "dev.json", # Renamed to dev.json
            "test.txt": "test.json"
        }

        for src_txt_file, dest_json_filename in file_mappings.items():
            source_txt_path = os.path.join(multiclass_path, src_txt_file)
            output_json_path = os.path.join(output_dataset_path, dest_json_filename)
            
            process_text_file_to_json(source_txt_path, output_json_path, tag_to_id_map)



def main():
    parser = argparse.ArgumentParser(
        description="Transform hierarchical text data into a new hierarchical JSON structure for NER tasks."
    )
    parser.add_argument(
        "--input-dir", 
        required=True, 
        help="Path to the source directory containing datasets (e.g., CBMA, CDBE)."
    )
    parser.add_argument(
        "--output-dir", 
        required=True, 
        help="Path to the destination directory where the transformed JSON files will be saved."
    )
    parser.add_argument(
        "--output-prefix", 
        default="", 
        help="Optional prefix string to add to output dataset directory names (e.g., 'transformed-')."
    )
    parser.add_argument(
        "--output-suffix", 
        default="", 
        help="Optional suffix string to add to output dataset directory names (e.g., '_processed')."
    )

    args = parser.parse_args()

    transform_data_to_json_format(args.input_dir, args.output_dir, args.output_prefix, args.output_suffix)


if __name__ == "__main__":
    main()
