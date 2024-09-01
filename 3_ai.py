import google.generativeai as genai
import os, re
import shutil


genai.configure(api_key="INSERT_YOUR_API_KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

import os
import PyPDF2

# Define the prompt template
prompt = lambda content: f"Based on the following content, provide a category, sender of the letter and a short title (max 5 words each) separated by a comma. Here are some examples first: output_10_FINANCE_KANTONALES_STEUERAMT_TAX_REFUND_STATEMENT.pdf, output_11_TAX_NOTICE_KANTONALES_STEUERAMT_TAX_REMINDER.pdf, output_21_HEALTHCARE_SWICA_REGIONAL_DIRECTORY.pdf And here is the content:\n\n{content}"

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text[:1000]  # Limit to first 1000 characters to avoid token limits

def rename_pdf(pdf_path):
    # Extract text from PDF
    src_file_path = os.path.join("2_Split", pdf_path)
    content = extract_text_from_pdf(os.path.join("2_Split", pdf_path))

    # Generate category and title using LLM
    response = model.generate_content(prompt (content))
    category, sender, title = response.text.split(',')

    # Clean up category and title
    category = category.strip().replace(' ', '_').upper()
    title = title.strip().replace(' ', '_').upper()
    sender = sender.strip().replace(' ', '_').upper()

    # Get the old filename and directory
    directory, old_filename = os.path.split(pdf_path)
    name, ext = os.path.splitext(old_filename)

    # Create the new filename
    new_filename = f"{name}_{category}_{sender}_{title}{ext}"

    # Create the full new path
    dst_file_path = os.path.join("3_AI", new_filename)

    # Rename the file
    shutil.copy2(src_file_path, dst_file_path)
    print(f"File renamed to: {new_filename}")

def process_directory():
    # Regex pattern to match "output_NUMBER.pdf" files
    pattern = re.compile(r'output_\d+\.pdf')

    # Iterate through all files in the directory
    for filename in os.listdir("2_Split"):
        if pattern.match(filename):
            pdf_path = filename
            dest_file_name = pdf_path [:-4]
            if file_exists (dest_file_name):
                continue
            try:
                rename_pdf(pdf_path)
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")

def file_exists(dest_file_name):
    dest_pattern = re.compile(f'{dest_file_name}_.*\\.pdf')
    for filename in os.listdir("3_AI"):
        if dest_pattern.match(filename):
            print (f"Already converted to: {filename}")
            return True
    return False

if __name__ == "__main__":
    process_directory()