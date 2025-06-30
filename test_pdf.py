#!/usr/bin/env python3
import pdfplumber
import os

def test_pdf_extraction():
    print("Testing PDF text extraction...")
    
    pdf_path = "test_document.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"✗ PDF file not found: {pdf_path}")
        return
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"✓ PDF opened successfully. Pages: {len(pdf.pages)}")
            
            text = ""
            for i, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                print(f"Page {i+1}: {len(page_text) if page_text else 0} characters")
                if page_text:
                    text += page_text + "\n"
            
            print(f"\nTotal extracted text length: {len(text)} characters")
            if text.strip():
                print("✓ Text extracted successfully")
                print(f"First 200 characters: {text[:200]}...")
            else:
                print("✗ No text extracted from PDF")
                
    except Exception as e:
        print(f"✗ Error extracting text: {e}")

if __name__ == "__main__":
    test_pdf_extraction() 