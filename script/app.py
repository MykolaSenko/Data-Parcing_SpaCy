import spacy  # NLP library
import csv    # For writing CSV files
from spacy.matcher import Matcher  # For pattern matching in spaCy
import re     # Regular expressions
import os     # File and directory operations

# Read binary file and split by null byte
def read_fields(filepath):
    """
    Reads a binary file, splits it by null byte, decodes each field, and returns a list of strings.
    """
    with open(filepath, 'rb') as f:
        binary_content = f.read()
    fields = binary_content.split(b'\\x00')
    all_fields = []
    for field in fields:
        if field:
            text = field.decode('latin-1').strip()
            all_fields.append(text)
    return all_fields

# Process a chunk of fields into a record
def process_chunk(chunk):
    """
    Processes a chunk of fields and extracts structured record data using spaCy and regex.
    """
    # Define the expected headers for the output CSV
    headers = [
        "Serial Number", "Part Number", "Part Name English", 
        "Part Name Language 1", "Part Name Language 2", "Part Name Language 3", 
        "Part Name Language 4", "Part Name Language 5", 
        "Part Number in Other Format", "Reference Number", 
        "Additional Information", "Extra Data"
    ]
    record = {h: '' for h in headers}
    # The first item is always the Serial Number
    record['Serial Number'] = chunk[0]
    data_fields = chunk[1:]
    if not data_fields:
        return record
    # Join fields for NLP processing
    chunk_text = "\n".join(chunk)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(chunk_text)
    matcher = Matcher(nlp.vocab)
    # Add matcher patterns for part numbers and reference numbers
    part_number_pattern = [{"TEXT": {"REGEX": r"^(?=.*\d)[A-Z0-9]{12,13}$"}}]
    matcher.add("Part Number", [part_number_pattern])
    other_part_number_pattern = [{"TEXT": {"REGEX": r"^(?=.*\d)(?=.*\.)([A-Z0-9.]{15,16})$"}}]
    matcher.add("Part Number in Other Format", [other_part_number_pattern])
    reference_number_pattern = [{"TEXT": {"REGEX": r"^[0-9]{8}$"}}]
    matcher.add("Reference Number", [reference_number_pattern])
    # Find matches in the doc
    matches = matcher(doc)
    first_matches = {}
    # Only keep the first occurrence of each label
    for match_id, start, end in matches:
        label = nlp.vocab.strings[match_id]
        if label not in first_matches:
            first_matches[label] = doc[start:end]
    for label, span in first_matches.items():
        record[label] = span.text
    # Determine where to start extracting names
    if record['Serial Number'] == '20':
        current_pos = 0
    else:
        current_pos = 1
    names_end_pos = current_pos
    # Find the end of the variable-length name fields
    for i in range(current_pos, len(data_fields)):
        field = data_fields[i]
        is_formatted_part_num = bool(re.match(r"^(?=.*\d)(?=.*\.)([A-Z0-9.]{15,16})$", field))
        is_ref_num = bool(re.match(r"^[0-9]{8}$", field))
        if is_formatted_part_num or is_ref_num:
            break
        names_end_pos += 1
    names = data_fields[current_pos:names_end_pos]
    # Assign names to the correct columns
    name_headers = headers[2:8]
    mapping = {
        0: "Part Name Language 2",
        1: "Part Name English",
        2: "Part Name Language 4",
        3: "Part Name Language 1",
        4: "Part Name Language 3",
        5: "Part Name Language 5",
    }
    for i, name in enumerate(names):
        if record['Serial Number'] == '20':
            if i in mapping:
                record[mapping[i]] = name
        else:
            if i < len(name_headers):
                record[name_headers[i]] = name
    # Find position for additional information
    if record.get('Reference Number'):
        current_pos = int(chunk.index(record['Reference Number']))
    elif record.get('Part Number in Other Format'):
        current_pos = int(chunk.index(record['Part Number in Other Format']))
    else:
        current_pos = 0
    # Assign additional information if present
    if current_pos < len(data_fields) and data_fields[current_pos] not in names:
        record['Additional Information'] = data_fields[current_pos]
        current_pos += 1
    # Special handling for record 61
    if record['Serial Number'] == '61':
        data_fields[current_pos:] = []
    extra_data = []
    # Any remaining fields are considered extra data
    if current_pos < len(data_fields) and data_fields[current_pos] not in names:
        extra_data = data_fields[current_pos:]
    if extra_data:
        record['Extra Data'] = '___'.join(extra_data)
    else:
        record['Extra Data'] = '-'
    return record

def main():
    """
    Main function to read the input file, process all records, and write output to CSV.
    """
    # Read and decode all fields from the input file
    all_fields = read_fields("source/Input_File_01.txt")
    # Find indices where a new record starts (serial numbers)
    start_indices = []
    for i, field in enumerate(all_fields):
        if field.isdigit() and len(field) < 4:
            start_indices.append(i)
    records_data = []
    # Process each chunk between serial numbers
    for i in range(len(start_indices)):
        start = start_indices[i]
        end = start_indices[i + 1] if i + 1 < len(start_indices) else len(all_fields)
        chunk = all_fields[start:end]
        if chunk:
            processed_chunk = process_chunk(chunk)
            records_data.append(processed_chunk)
    # Write results to CSV if any records found
    if not records_data:
        print("No records to write.")
        return
    os.makedirs('output', exist_ok=True)
    with open('output/output_spacy.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=records_data[0].keys())
        writer.writeheader()
        writer.writerows(records_data)
        print("Data successfully written to 'output/output_spacy.csv'")