import json
import os
# import re # Not strictly needed for the current email parsing

def extract_email_domain(email_address):
    """
    Extracts the domain from an email address.
    Returns None if the email_address is None, empty, or malformed.
    """
    if not email_address or not isinstance(email_address, str):
        return None
    parts = email_address.split('@')
    if len(parts) == 2 and parts[1]: # Ensure there's something after @
        return parts[1]
    # print(f"Warning: Could not extract domain from email: {email_address}") # Optional warning during development
    return None

def transform_record(record_str, input_filepath, line_number):
    """
    Transforms a single JSON record string.
    Logs errors to console and 'error_log.txt'.
    """
    try:
        record = json.loads(record_str)
    except json.JSONDecodeError as e:
        error_message = (f"Warning: Line {line_number} in {input_filepath} - "
                         f"Could not decode JSON: {record_str[:100]}... - Error: {e}")
        print(error_message)
        with open("error_log.txt", "a", encoding="utf-8") as error_log:
            error_log.write(error_message + "\n")
        return None # Skip malformed lines

    # Rule 1: Remove PII
    record.pop('C_FIRST_NAME', None)
    record.pop('C_LAST_NAME', None)

    # Rule 2: Email transformation
    email_address = record.pop('C_EMAIL_ADDRESS', None)
    if email_address:
        domain = extract_email_domain(email_address)
        record['C_EMAIL_DOMAIN'] = domain
    else:
        record['C_EMAIL_DOMAIN'] = None # Ensure field exists even if source email was missing
        
    return record

def process_file(input_filepath, output_filepath):
    """
    Processes a single input file and writes transformed records to an output file.
    """
    print(f"Processing {input_filepath} -> {output_filepath}...")
    processed_lines = 0
    error_lines = 0
    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile, \
             open(output_filepath, 'w', encoding='utf-8') as outfile:
            for line_num, line_content in enumerate(infile, 1):
                stripped_line = line_content.strip()
                if not stripped_line: # Skip empty lines
                    continue
                
                transformed_record = transform_record(stripped_line, input_filepath, line_num)
                
                if transformed_record:
                    json.dump(transformed_record, outfile)
                    outfile.write('\n')
                    processed_lines += 1
                else:
                    error_lines += 1
        print(f"Successfully processed {input_filepath}. Lines written: {processed_lines}, Lines with errors: {error_lines}")
    except FileNotFoundError:
        print(f"Error: Input file not found: {input_filepath}")
    except IOError as e:
        print(f"Error processing file {input_filepath}: {e}")

def main():
    source_data_dir = os.path.join('data', 'data-exports', 'TPCDS_SF10TCL', 'customer')
    output_data_dir = 'output_data'

    print(f"Source data directory: '{source_data_dir}'")
    print(f"Output data directory: '{output_data_dir}'")

    if not os.path.exists(source_data_dir):
        print(f"Error: Source data directory '{source_data_dir}' does not exist.")
        return
    if not os.path.isdir(source_data_dir):
        print(f"Error: Source data path '{source_data_dir}' is not a directory.")
        return

    if not os.path.exists(output_data_dir):
        try:
            os.makedirs(output_data_dir)
            print(f"Created output directory: '{output_data_dir}'")
        except OSError as e:
            print(f"Error creating output directory '{output_data_dir}': {e}")
            return
    
    files_to_process = [f for f in os.listdir(source_data_dir) if f.endswith(".txt")]

    if not files_to_process:
        print(f"No .txt files found in '{source_data_dir}'.")
        return

    print(f"Found .txt files to process: {files_to_process}")

    for filename in files_to_process:
        input_filepath = os.path.join(source_data_dir, filename)
        
        base, ext = os.path.splitext(filename)
        output_filename = f"{base}_transformed{ext}"
        output_filepath = os.path.join(output_data_dir, output_filename)
        
        process_file(input_filepath, output_filepath)
            
    print("\nAll files processed.")

if __name__ == "__main__":
    main()