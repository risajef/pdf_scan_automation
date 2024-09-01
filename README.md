# In Short
1. Takes scans of multiple documents. 
2. Makes OCR (and deskews the pages using tesaract)
3. Splits the up into individual documents. Using a predefined separator page. (Removes all separator pages and empty pages)
4. Gives the documents sensible titles using AI

# Instructions
1. Put documents in `0_Scans`
2. Run `python 1_ocr.py` -- The documents should have the form `NextDocument.*.pdf`
3. Run `python 2_split.py` -- The separator page is `separator.pdf` and can be replaced.
3. Run `python 3_ai.py` -- Uses an API-Key to Google. Please insert your own else it will not work.

# Libraries
The `requirements.txt` was produced using `pip freeze > requirements.txt`. I don't think all the libraries are needed.