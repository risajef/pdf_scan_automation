import os, re, numpy as np
import cv2
import glob
import pymupdf

def is_empty_page(page, brightness_threshold=0.95, edge_threshold=0.01, content_threshold=0.01):
    # Convert PDF page to image
    pix = page.get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
    
    # Convert to grayscale if it's not already
    if img.shape[2] == 3:
        img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    else:
        img_gray = img[:,:,0]
    
    # Check overall brightness
    brightness = np.mean(img_gray) / 255.0
    if brightness < brightness_threshold:
        return False
    
    # Check for edges
    edges = cv2.Canny(img_gray, 100, 200)
    edge_percentage = np.sum(edges > 0) / (img_gray.shape[0] * img_gray.shape[1])
    if edge_percentage > edge_threshold:
        return False
    
    # Check percentage of non-white pixels
    non_white_percentage = np.sum(img_gray < 250) / (img_gray.shape[0] * img_gray.shape[1])
    if non_white_percentage > content_threshold:
        return False
    
    return True
def get_page_image(page):
    pix = page.get_pixmap()
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)

    # if img.shape[2] == 3:
    #     return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    return img[:,:,:]

# Load the separator page PDF once
separator_image = get_page_image(pymupdf.open("separator.pdf")[0])
def get_next_doc_number(output_prefix):
    existing_files = [f for f in os.listdir("2_Split") if f.startswith(output_prefix) and f.endswith('.pdf')]
    if not existing_files:
        return 1
    
    numbers = [int(re.search(r'(\d+)\.pdf$', f).group(1)) for f in existing_files]
    return max(numbers) + 1
def compare_images_features(img1, img2):
    orb = cv2.ORB_create()
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    if (des1 is None or des2 is None):
        return 0
    matches = bf.match(des1, des2)
    
    good_matches = [m for m in matches if m.distance < 50]
    return len(good_matches)  # Adjust threshold as needed

def is_separator_page(page):
    img = get_page_image (page)

    # Resize both images to the same dimensions
    separator_resized = cv2.resize(separator_image, (img.shape[1], img.shape[0]))
    # Compute the structural similarity index
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    separator_gray = cv2.cvtColor(separator_resized, cv2.COLOR_BGR2GRAY)

    # Compute the Structural Similarity Index (SSIM)
    # (score, diff) = structural_similarity(img_gray, separator_gray, full=True, win_size=9)
    
    # You may need to adjust this threshold based on your specific case
    return compare_images_features (separator_gray, img_gray) > 50
def split_pdf(input_path, output_prefix, base_dir):
    # Now split the deskewed PDF
    doc = pymupdf.open(input_path)
    current_doc = pymupdf.open()
    doc_number = get_next_doc_number(output_prefix)

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        if is_separator_page(page):
            if current_doc.page_count > 0:
                current_doc.save(os.path.join("2_Split", f"{output_prefix}_{doc_number}.pdf"))
                current_doc.close()
                current_doc = pymupdf.open()
                doc_number += 1
        elif not is_empty_page(page):
            current_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    # Save the last document
    if current_doc.page_count > 0:
        current_doc.save(os.path.join("2_Split", f"{output_prefix}_{doc_number}.pdf"))
        current_doc.close()

    doc.close()

    # Tag the document as splitted
    _, filename = os.path.split (input_path)
    os.rename (input_path, os.path.join(base_dir, "1_OCR", f"SPLITTED_{filename}"))

def process_all_next_documents():
    # Get the current directory
    current_dir = os.getcwd()

    # Find all files matching the pattern
    input_files = glob.glob(os.path.join(current_dir, "1_OCR", "OCR_NextDocument*.pdf"))

    # Loop through each file
    for input_file in input_files:
        # Call the conversion function
        split_pdf(input_file, "output", current_dir)

    print("All OCR_NextDocument*.pdf files have been processed.")

# Run the function
if __name__ == "__main__":
    process_all_next_documents()