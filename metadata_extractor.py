#import cv2
#import pytesseract
#import re
#from datetime import datetime
#from dateutil import parser

import cv2
import pytesseract
import numpy as np
import logging
from io import BytesIO

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

def extract_metadata(file_obj):
    try:
        # Read the image file
        file_bytes = file_obj.read()
        
        # Convert to numpy array
        nparr = np.frombuffer(file_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            logger.error("Failed to decode image")
            return {"error": "Could not decode the image"}
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Extract text
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(gray, config=custom_config)
        
        if not text.strip():
            logger.error("No text could be extracted from the image")
            return {"error": "No text could be extracted from the image"}
            
        # Process the extracted text
        # ... (rest of your existing code)
        
        return {
            "title": "Sample Title",  # Replace with actual extraction
            "authors": ["Author 1"],  # Replace with actual extraction
            "isbn": "1234567890",     # Replace with actual extraction
            "text_sample": text[:200]  # Return first 200 chars for debugging
        }
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"error": f"Error processing image: {str(e)}"}
        