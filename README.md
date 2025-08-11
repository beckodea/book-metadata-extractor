# Book Metadata Extractor

A web application that extracts metadata from book images using OCR and outputs the results in JSON format.

## Features

- Extracts metadata from book cover images and title pages
- Supports multiple image uploads (batch processing)
- Extracts the following metadata:
  - Title
  - Authors
  - ISBN (10 or 13 digits)
  - Publishers
  - Publication date
  - Edition
- Responsive web interface with drag-and-drop support
- Outputs clean, structured JSON data

## JSON Schema

The extracted metadata follows this schema:

```json
{
  "title": "string | null",
  "authors": ["string"],
  "isbn": "string | null",
  "publishers": ["string"],
  "publication_date": "string | null",
  "edition": "string | null",
  "filename": "string"
}
```

## Installation

1. **Install Tesseract OCR**
   - Windows: Download and install from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Linux: `sudo apt install tesseract-ocr`

2. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book_metadata_extractor
   ```

3. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

4. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**
   ```bash
   python app.py
   ```

2. **Open your web browser**
   Visit `http://localhost:5000`

3. **Upload book images**
   - Drag and drop images or click to select files
   - Click "Process Images" to extract metadata

## Dependencies

- Python 3.7+
- Tesseract OCR
- Flask
- pytesseract
- opencv-python
- Pillow
- python-dateutil

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
