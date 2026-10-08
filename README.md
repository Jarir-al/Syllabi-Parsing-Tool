# Syllabi-Parsing-Tool
Syllabus Parsing using deterministic preprocessing and hueristics and a generative foundation model with structured output. 

## Extract Raw Text (Extract_raw.py)
Using PDF Plumber we first format tables into readable text for our LLM to analyze.

Then extracts pdf text and tables into a page_content which is appended into the full page_content data structure and then outputs it into raw_output.txt. 

## Trimming text to lower input tokens (trimmer.py)
Adds text to output file if a block has an adequate score which is determined by the presence of keywords. Also trims extraneous tables if a high ratio of cid exists

## Scehma (Schema.py)
Contains Schema which will be used by the extractor.py file and the LLM to extract adequate information into the class file

## Extractor (Extractor.py)
Uses the latest flash model or gemini 3.5 if latest flash model does not exist