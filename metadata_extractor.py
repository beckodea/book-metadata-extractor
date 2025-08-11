import cv2
import pytesseract
import re
from datetime import datetime
from dateutil import parser

def preprocess_image(image_path):
    """Preprocess the image for better OCR results."""
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # Apply dilation to connect text components
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    gray = cv2.dilate(gray, kernel, iterations=1)
    
    return gray

def extract_text(image_path):
    """Extract text from image using Tesseract OCR."""
    try:
        # Preprocess the image
        processed_img = preprocess_image(image_path)
        
        # Use Tesseract to extract text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(processed_img, config=custom_config)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {str(e)}")
        return ""

def extract_isbn(text):
    """Extract ISBN from text using regex patterns."""
    # Common ISBN patterns (10 or 13 digits, with optional hyphens/spaces)
    isbn_patterns = [
        r'\b(?:ISBN(?:-1[03])?:?\s*)?(97[89][-\s]?\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,6}[-\s]?\d)\b',  # ISBN-13
        r'\b(?:ISBN(?:-10)?:?\s*)?(\d{1,5}[-\s]?\d{1,7}[-\s]?\d{1,6}[-\s]?[\dX])\b'  # ISBN-10
    ]
    
    for pattern in isbn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Clean up the matched ISBN
            isbn = re.sub(r'[^\dX]', '', match.group(1)).upper()
            # Validate ISBN length (10 or 13 digits)
            if len(isbn) in (10, 13):
                return isbn
    return None

def extract_publication_date(text):
    """Extract publication date from text."""
    # Look for years in the text (1900-2099)
    year_matches = re.findall(r'\b(19\d{2}|20[0-9]{2})\b', text)
    if year_matches:
        try:
            # Get the most recent year (likely the publication year)
            years = [int(y) for y in year_matches]
            most_recent_year = max(years)
            # Only return if it's a reasonable year
            if 1900 <= most_recent_year <= datetime.now().year + 1:
                return str(most_recent_year)
        except (ValueError, IndexError):
            pass
    return None

def extract_metadata(image_path):
    """Extract metadata from book image."""
    # Extract text from image
    text = extract_text(image_path)
    if not text:
        return {"error": "No text could be extracted from the image"}
    
    # Initialize metadata
    metadata = {
        "title": None,
        "authors": [],
        "isbn": None,
        "publishers": [],
        "publication_date": None,
        "edition": None,
        "extracted_text": text[:1000] + "..." if len(text) > 1000 else text  # Store first 1000 chars for debugging
    }
    
    # Extract ISBN
    metadata["isbn"] = extract_isbn(text)
    
    # Extract publication date
    metadata["publication_date"] = extract_publication_date(text)
    
    # For title and authors, we'll use some heuristics
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # First non-empty line is often the title
    if lines:
        metadata["title"] = lines[0]
    
    # Look for author names (this is a very basic approach)
    author_keywords = ['by ', 'author', 'written by', 'edited by']
    for line in lines[1:5]:  # Check first few lines for authors
        if any(keyword in line.lower() for keyword in author_keywords):
            # Clean up the line to extract just the name
            author = re.sub(r'(?i)(by|author|written by|edited by)[: ]*', '', line, flags=re.IGNORECASE).strip()
            if author and len(author) < 100:  # Sanity check
                metadata["authors"].append(author)
    
    # Look for edition information
    edition_patterns = [
        r'(\d+)(?:st|nd|rd|th)\s+(?:edition|ed\.|ed\b)',
        r'(?:edition|ed\.|ed\b)\s*(\d+)',
        r'\b(\d+)(?:st|nd|rd|th)\s+ed\.?\b'
    ]
    
    for line in lines:
        for pattern in edition_patterns:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                metadata["edition"] = match.group(1)
                break
        if metadata["edition"]:
            break
    
    # Clean up empty fields
    metadata = {k: v for k, v in metadata.items() if v not in (None, [], "")}
    return metadata
