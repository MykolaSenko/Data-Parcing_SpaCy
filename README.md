# SpaCy Data Parsing Experiment

This repository demonstrates how to parse a binary text file, extract structured records, and write the results to a CSV file using SpaCy and Python.

## Features
- Reads binary input files and splits data by null-byte delimiters
- Uses SpaCy for NLP and pattern matching to extract part numbers, reference numbers, and names
- Handles variable-length records and edge cases
- Outputs structured data to a CSV file for further analysis
- Includes both a Jupyter Notebook (`tests.ipynb`) and a standalone Python script (`app.py`)

## File Structure
```
SpaCy_experiment/
├── source/
│   └── Input_File_01.txt         # Example binary input file
├── output/
│   └── output_spacy.csv          # Output CSV file (created after running)
├── tests.ipynb                   # Jupyter Notebook with step-by-step workflow
├── app.py                        # Standalone Python script for batch processing
├── requirements.txt              # Python dependencies
```

## Usage

### 1. Jupyter Notebook
Open `tests.ipynb` in VS Code or Jupyter Lab/Notebook and run the cells step by step. The notebook is commented and includes markdown explanations for each stage.

### 2. Python Script
Run the entire workflow from the command line:
```bash
python3 app.py
```
This will process `source/Input_File_01.txt` and write results to `output/output_spacy.csv`.

## Requirements
- Python 3.12
- SpaCy
- en_core_web_sm model
- VS Code (recommended for notebook and script editing)

Run the Development Container to ensure all dependencies are correctly set up.

## Extensions (Recommended for VS Code)
- Hex Editor (ms-vscode.hexeditor): View binary files
- Jupyter (ms-toolsai.jupyter): Run notebooks
- Python (ms-python.python): Python support
- CSV and Excel Viewer (GrapeCity.gc-excelviewer): View CSV files
- Data Wrangler (ms-toolsai.datawrangler): Data manipulation and transformation

## How it works

The workflow for parsing and extracting structured data from the binary input file is as follows:

1. **Read the Input File**
   - The input file (`Input_File_01.txt`) is read in binary mode.
   - The file is split into fields using the null-byte (`\x00`) delimiter.
   - Each field is decoded from bytes to a string and stripped of whitespace.

2. **Identify Record Boundaries**
   - Records are identified by short digit fields (serial numbers) in the data.
   - The indices of these serial numbers are used to split the data into chunks, each representing a record.

3. **Process Each Record Chunk**
   - For each chunk, the first field is treated as the serial number.
   - The remaining fields are processed to extract part numbers, reference numbers, and variable-length name fields.
   - SpaCy's NLP model and matcher are used to find part numbers and reference numbers using regular expressions.
   - The logic handles special cases, such as records with missing fields or variable name mappings (e.g., record #20).
   - Additional information and extra data are extracted based on their position and content.

4. **Structure the Data**
   - Each processed chunk is converted into a dictionary with predefined headers.
   - Name fields are mapped to their respective columns, and extra data is joined with a separator or marked as missing.

5. **Write to CSV**
   - All processed records are written to an output CSV file (`output/output_spacy.csv`) for further analysis or sharing.

This approach ensures robust parsing of complex, variable-length records from binary files, leveraging both Python's string handling and SpaCy's NLP capabilities.

## License
MIT

## Author
Mykola Senko
September 21, 2025
Kortrijk, Belgium