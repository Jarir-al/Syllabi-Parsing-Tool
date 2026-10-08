import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schema import CourseSyllabus

load_dotenv()

def extract_with_gemini(cleaned_text: str) -> CourseSyllabus:
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    fprompt = f"""
You are an expert academic syllabus parser.
Extract the course details, instructor info, grading weights, and all deliverables/exams 
from the following syllabus text.

### CRITICAL PARSING RULES:
1. **Terminology Synonyms**:
   - Treat "Homework", "HW", "Programming Assignment", "PA", "Project", and "Lab" as deliverables according to their context. If the syllabus uses terms interchangeably (e.g., "Homework" in the grading breakdown but "Programming Assignment" on the calendar), map them accurately.

2. **Relative Dates & Day-of-Week Resolution**:
   - Syllabi often state policies like: "Programming assignments are due the Wednesday after they are assigned."
   - Cross-reference the class schedule or calendar dates. For each assigned homework/project, determine its release date, identify what day of the week that falls on, and compute the explicit date of the following Wednesday.
   - Infer the course year from the semester, calendar dates, or context (e.g., Fall/Spring) to correctly determine days of the week.
   - Format `due_date` as YYYY-MM-DD whenever the date can be derived. If the exact day cannot be calculated with certainty, record the exact stated policy or relative date phrase (e.g., "Wednesday after assigned (Week 3)").

3. **Grading & Weights**:
   - If grading weights are in raw points (e.g. 200/1000 or 150/1300), preserve raw points and normalize them to decimal percentages (0.0 to 1.0).

4. **Letter Grade Scale / Cutoffs**:
    - Extract the letter grade thresholds (e.g., A+: [97, 100], A: [93, 96.99], B: [83, 86.99]).
    - Store the verbatim range string in `raw_range` and parse the numerical threshold into `min_score` and `max_score`.
    - If no explicit scale is published in the document, return an empty list for `letter_grade_scale`.
    

Syllabus Content:
{cleaned_text}
"""
    
    # Cascade list of valid endpoints from your registry
    models_to_try = [
        "gemini-flash-latest",
        "gemini-3.5-flash"
    ]
    
    for model_name in models_to_try:
        for attempt in range(3):
            try:
                print(f"Calling {model_name} (attempt {attempt + 1})...")
                response = client.models.generate_content(
                    model=model_name,
                    contents=fprompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CourseSyllabus,
                        temperature=0.1,
                    ),
                )
                return CourseSyllabus.model_validate_json(response.text)
                
            except Exception as e:
                err_msg = str(e)
                if "503" in err_msg or "UNAVAILABLE" in err_msg:
                    wait_time = 2 * (attempt + 1)
                    print(f"503 traffic spike on {model_name}. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"Skipping {model_name}: {err_msg[:90]}...")
                    break  # Move to next model if it's a 404 or config error
                    
    raise RuntimeError("All models encountered errors or traffic limits.")

if __name__ == "__main__":
    with open("cleaned_output.txt", "r", encoding="utf-8") as f:
        syllabus_text = f.read()
        
    print("Extracting syllabus data...")
    syllabus_data = extract_with_gemini(syllabus_text)
    
    output_path = "syllabus_data.json"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(syllabus_data.model_dump_json(indent=2))
        
    print(f"\nExtraction complete! Output saved to '{output_path}'.")
    print(f"Course: {syllabus_data.course_code} - {syllabus_data.course_title}")
    print(f"Instructor: {syllabus_data.instructor}")
    print(f"Deliverables found: {len(syllabus_data.deliverables)}")
    print(f"Grading categories: {len(syllabus_data.grade_distribution)}")