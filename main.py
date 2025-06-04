import os, shutil, datetime, pdfplumber
import logging
import textwrap
from dotenv import load_dotenv
from pathlib import Path
from time import time
from colorama import Fore



################### API-KEY SETUP #######################

load_dotenv()  # This loads the .env file into the environment variables
api_key = os.getenv("OPENAI_API_KEY")

################### END OF API-KEY SETUP ################

################### AI HELPER FUNCTIONS #################
from litellm import completion
from typing import List, Dict

def generate_response(messages: List[Dict]) -> str:
    """Call LLM to get response"""
    response = completion(
        model="openai/gpt-4o",
        messages=messages,
        max_tokens=1024
    )
    return response.choices[0].message.content

############# END OF AI HELPER FUNCTIONS ################

############# CORE FUNCTIONS IN FILE ORGANIZER ##########

def get_list_all_files(directory_path) -> list:

    # Directory path can be a string or a Path object
    list_of_all_files = [p for p in Path(directory_path).iterdir() if p.is_file()]

    return list_of_all_files

def copy_or_move(file_path:Path, destination_dir: Path, move_files=False):
    if move_files:
        try:
            shutil.move(file_path, destination_dir/file_path.name)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied for file: {file_path}")
        except Exception as e:
            print(f"Unexpected error while moving {file_path}: {e}")
        return
    else:
        try:
            shutil.copy2(file_path, destination_dir)
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except PermissionError:
            print(f"Permission denied for file: {file_path}")
        except Exception as e:
            print(f"Unexpected error while moving {file_path}: {e}")
    

def add_subfolder(parent_dir:Path, subfolder:Path):
    # Create subfolder within parent_dir 
    # and returns path to subfolder as Path
    try:
        Path.mkdir(parent_dir/subfolder, exist_ok=True)
        return parent_dir/subfolder
    except PermissionError:
        print(f"Permission denied: {parent_dir/subfolder}")
    except OSError as e:
        print(f"OS error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def initialize_organized_dir(source_dir: Path):
    # Create "organized" folder within source_dir
    add_subfolder(source_dir, Path("organized"))

def measure_total_size(file_or_dir: Path) -> float:

     # If file: returns file size
    if file_or_dir.is_file():
        total_size = file_or_dir.stat().st_size
    
    # If directory: recursively walks and returns total size of files
    elif file_or_dir.is_dir():
        total_size = 0
        for root, dirs, files in file_or_dir.walk(on_error=print):
            total_size += sum((root / file).stat().st_size for file in files)
        
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
    
    # Otherwise prints an error and returns an invalid total_size=-1
    else:
        print("Something went wrong...")
        return -1

    return total_size

def get_creation_year(file_path: Path):
    # Gets year of file creation and returns it as a number
    file_timestamp = file_path.stat().st_birthtime
    creation_datetime = datetime.datetime.fromtimestamp(file_timestamp)
    creation_year = creation_datetime.date().year
    
    return creation_year
    

def get_file_extension(file_path: Path) -> str:
    return file_path.suffix.strip(".")

def find_oldest_pdf(original_folder: Path) -> Path:
    # Get a list of file Paths in the source_dir
    all_pdfs = [p for p in Path(original_folder).iterdir() if p.is_file() and get_file_extension(p) == "pdf"]
    oldest_file = min(all_pdfs, key=lambda f: f.stat().st_birthtime, default=None)
    
    print(textwrap.fill(Fore.YELLOW + f"The oldest file in this folder is: {oldest_file.name}. It was created on {datetime.datetime.fromtimestamp(oldest_file.stat().st_birthtime).day}.{datetime.datetime.fromtimestamp(oldest_file.stat().st_birthtime).month}.{datetime.datetime.fromtimestamp(oldest_file.stat().st_birthtime).year}.", width=80))
    print()
    return oldest_file

def find_newest_pdf(original_folder: Path) -> Path:
    # Get a list of file Paths in the source_dir
    all_pdfs = [p for p in Path(original_folder).iterdir() if p.is_file() and get_file_extension(p) == "pdf"]
    newest_file = max(all_pdfs, key=lambda f: f.stat().st_birthtime, default=None)
    
    print(textwrap.fill(Fore.YELLOW + f"The newest file in this folder is: {newest_file.name}. It was created on {datetime.datetime.fromtimestamp(newest_file.stat().st_birthtime).day}.{datetime.datetime.fromtimestamp(newest_file.stat().st_birthtime).month}.{datetime.datetime.fromtimestamp(newest_file.stat().st_birthtime).year}.", width=80))
    print()
    return newest_file

def read_pdf_contents(pdf_file: Path) -> str:
    text = ""

    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""

    return text

def analyze_file_with_ai(file_path: Path, context=""):
    # Here comes the call to ChatGPT API and its response
    pdf_contents = read_pdf_contents(file_path)
    messages = [
    {"role": "system", "content": "You are an expert librarian who knows about every possible subject and is very adept at creating brief and insightful summaries of data provided to you."},
    {"role": "assistant", "content": f"{context}"},
    {"role": "user", "content": f"Write a summary of the following content: {pdf_contents}"}
    ]

    response = generate_response(messages)
    print(Fore.CYAN + "Here is the summary of this file provided to you by ChatGPT:")
    print()
    print(Fore.WHITE + textwrap.fill(response, width=80))

    return response

################## END OF CORE FUNCTIONS ################

# Suppress pdfplumber/pdfminer warnings about missing CropBox
logging.getLogger("pdfminer").setLevel(logging.ERROR)

def organize_files(source_dir=Path.cwd(), sorted_folder="penis", sort_by_type=True, sort_by_year=True, \
                   move_files=False, analyze_oldest_pdf=False, analyze_newest_pdf=False):
    
    Fore.RESET
    # Start the timer
    print("Starting to sort...")
    start_time = time()
    # Check if sorting is required by user at all
    if not sort_by_type and not sort_by_year:
        print(f"Sort by type is {sort_by_type}, sort by year is {sort_by_year}, therefore nothing to sort.")
        return
    # In case source_dir is given as string, convert it to Path:
    source_dir = Path(source_dir)    
    # Initialize folder name for "organized" folder
    sorted_folder = Path(sorted_folder)
    # Create "organized" folder
    work_dir = add_subfolder(source_dir, sorted_folder)
    # Get a list of file Paths in the source_dir
    list_of_all_files = get_list_all_files(source_dir)
    # Measure total size of all files in the list, total_source_size
    total_source_size = sum([measure_total_size(file_obj) for file_obj in list_of_all_files])
    
    if sort_by_type and sort_by_year:
        for file_path in list_of_all_files:
            # Get file extension and creation year as strings
            ext_str = get_file_extension(file_path)
            year_str = str(get_creation_year(file_path))
            # Create subfolder: file_extension/creation_year/ step by step
            ext_path = add_subfolder(work_dir, Path(ext_str))
            year_path = add_subfolder(ext_path, Path(year_str))
            # Copy or move the file to the subfolder
            copy_or_move(file_path, year_path, move_files=move_files)
    elif sort_by_type and not sort_by_year:
        for file_path in list_of_all_files:
            # Get only file extension as string
            dest_str = get_file_extension(file_path)
            dest_path = add_subfolder(work_dir, Path(dest_str))
            copy_or_move(file_path, dest_path, move_files=move_files)
    elif sort_by_year and not sort_by_type:
        for file_path in list_of_all_files:
            # Get only creation year as string
            dest_str = str(get_creation_year(file_path))
            dest_path = add_subfolder(work_dir, Path(dest_str))
            copy_or_move(file_path, dest_path, move_files=move_files)
    

    total_organized_size = measure_total_size(work_dir)
    end_time = time()
    print("Finished sorting.")
    print()
    if total_source_size != total_organized_size:
        print(f"WARNING! Size of all original files: {total_source_size}. Size of all sorted files: {total_organized_size}.")
    else:
        print(f"ALL GOOD. Size of all original files: {total_source_size//1024**3} GB. Size of all sorted files: {total_organized_size//1024**3} GB.")
        print(f"Sorted {len(list_of_all_files)} files in {int(end_time - start_time)} seconds.\n")

    # OPTIONAL: Analysis of PDF files with ChatGPT API
    if analyze_oldest_pdf == True:
        oldest_pdf = find_oldest_pdf(source_dir)
        analyze_file_with_ai(oldest_pdf)
        print()

    if analyze_newest_pdf == True:
        
        newest_pdf = find_newest_pdf(source_dir)
        analyze_file_with_ai(newest_pdf)
        print()


if __name__ == "__main__":
    
   
    my_folder = Path(input("Enter the full path to the directory you wish to sort: "))
    organize_files(my_folder, analyze_oldest_pdf=True, analyze_newest_pdf=True)
    








