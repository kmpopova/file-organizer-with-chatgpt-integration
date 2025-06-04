# File Organizer with AI Analysis

This project is a Python-based file organizer that automatically sorts your files into subfolders based on their type and creation date. It also integrates with ChatGPT (optional) to provide AI-powered summaries of your oldest and newest PDF files.

## Features
- **Automatic File Organization:**
  - Sorts files (excluding folders) into subfolders by file type and creation year.
  - Supports both copying and moving files.
- **AI Integration:**
  - (Optional) After organizing, the app uses ChatGPT to generate an optional summary of your oldest and/or newest PDF file in the directory.
- **Customizable:**
  - Easily configure the source directory, sorting options, and whether to move or copy files.

## How It Works
1. The script scans the specified directory for files.
2. Files are sorted into an `organized` subfolder, grouped by type and/or year.
3. Optional: The oldest/newest PDF file is identified and its contents are summarized using ChatGPT (requires an OpenAI API key).

## Files
- `main.py` — Main script containing the file organization logic and AI integration.
- `.env` — Store your OpenAI API key and other environment variables here (not included in version control).
- `requirements.txt` — Lists all Python dependencies needed to run the project. Install these with `pip install -r requirements.txt`.
- `README.md` — Project documentation.

## Requirements
- Python 3.8+
- `openai` or compatible ChatGPT API client
- `python-dotenv`
- `pdfplumber`

## Usage
1. Clone the repository and install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Add your OpenAI API key to a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```
3. Run the script:
   ```sh
   python main.py
   ```

## Customization
- Edit `main.py` to change the source directory, sorting options, or AI summary behavior.

## License
This project is for educational and personal use (MIT License). See LICENSE for details.