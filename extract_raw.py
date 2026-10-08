import pdfplumber

def format_table(table):
    """Converts a 2D list of extracted table cells into readable text."""
    rows = []
    for row in table:
        # Filter out None values and clean whitespace
        cleaned_cells = [str(cell).strip() if cell else "" for cell in row]
        if any(cleaned_cells):  # Only keep non-empty rows
            rows.append(" | ".join(cleaned_cells))
    return "\n".join(rows)

def extract_pdf_content(pdf_path: str):
    full_output = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Loaded '{pdf_path}' with {len(pdf.pages)} pages.\n")
        
        for page_idx, page in enumerate(pdf.pages):
            page_num = page_idx + 1
            print(f"Processing Page {page_num}...")
            
            page_content = [f"\n=== Page {page_num} ==="]
            
            # 1. Extract regular text
            text = page.extract_text()
            if text:
                page_content.append(text)
                
            # 2. Extract tables (crucial for grading scales & schedules)
            tables = page.extract_tables()
            if tables:
                print(f"  -> Found {len(tables)} table(s) on Page {page_num}")
                page_content.append("\n--- Extracted Tables ---")
                for t_idx, table in enumerate(tables):
                    formatted = format_table(table)
                    if formatted:
                        page_content.append(f"[Table {t_idx + 1}]\n{formatted}")
            
            full_output.append("\n".join(page_content))

    return "\n".join(full_output)

if __name__ == "__main__":
    pdf_filename = "Syll2.pdf"
    
    # Run extraction
    content = extract_pdf_content(pdf_filename)
    
    # Save the output
    output_filename = "raw_output.txt"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"\nDone! Inspect '{output_filename}' to see how the layout held up.")