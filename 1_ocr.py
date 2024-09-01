import ocrmypdf
from typing import Optional
import os
import glob

def convert_pdf_with_ocr(
    input_pdf: str,
    output_pdf: str,
    language: str = 'eng',
    output_type: str = 'pdf',
    deskew: bool = True,
    clean: bool = True,
    rotate_pages: bool = True,
    tesseract_timeout: Optional[int] = None,
    tesseract_pagesegmode: Optional[int] = None
) -> None:
    try:
        ocrmypdf.ocr(
            input_pdf,
            output_pdf,
            language=language,
            output_type=output_type,
            deskew=deskew,
            clean=clean,
            rotate_pages=rotate_pages,
            tesseract_timeout=tesseract_timeout,
            tesseract_pagesegmode=tesseract_pagesegmode
        )
        print("OCR completed successfully")
    except ocrmypdf.exceptions.PriorOcrFoundError:
        print("Input PDF already contains OCR text")
    except ocrmypdf.exceptions.EncryptedPdfError:
        print("Input PDF is encrypted")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def process_all_next_documents():
    # Get the current directory
    current_dir = os.getcwd()

    # Find all files matching the pattern
    input_files = glob.glob(os.path.join(current_dir, "0_Scans", "NextDocument*.pdf"))

    # Loop through each file
    for input_file in input_files:
        # Generate the output filename
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        output_path = os.path.join(current_dir, "1_OCR", f"OCR_{base_name}.pdf")
        if (os.path.exists(output_path)):
            continue

        print(f"Processing: {input_file}")
        
        # Call the conversion function
        convert_pdf_with_ocr(input_file, output_path, language="deu", output_type="pdfa")

        print(f"Completed: {output_path}")

    print("All NextDocument*.pdf files have been processed.")

# Run the function
if __name__ == "__main__":
    process_all_next_documents()