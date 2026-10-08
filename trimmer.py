import re

RELEVANT_KEYWORDS = {
    # Grading & Weights
    "grade", "grading", "weight", "percent", "%", "points", "scale", "distribution",
    # Deliverables & Exams
    "assignment", "exam", "midterm", "final", "quiz", "project", "homework", "lab", "due",
    # Schedule & Timing
    "week", "date", "schedule", "calendar", "deadline", "october", "november", "december",
    # Course Identifiers
    "instructor", "professor", "office hours", "email", "prerequisite", "textbook"
}

def clean_cid_artifacts(text: str) -> tuple[str, bool]:
    """
    Checks if text is overwhelmingly corrupted by (cid:x) font errors.
    Returns (cleaned_text, is_usable).
    """
    cid_matches = re.findall(r"\(cid:\d+\)", text)
    if not cid_matches:
        return text, True
    
    # Calculate how much of the string is taken up by cid artifacts
    total_cid_chars = sum(len(m) for m in cid_matches)
    corruption_ratio = total_cid_chars / max(len(text), 1)
    
    # If more than 35% of the text is (cid:x) artifacts, it's garbage
    if corruption_ratio > 0.35:
        return "", False
        
    # Otherwise, simply remove the (cid:x) noise and keep the readable words
    cleaned = re.sub(r"\(cid:\d+\)", " ", text)
    return cleaned, True

def split_into_blocks(raw_text: str) -> list[str]:
    """
    Robust splitting that handles both \n\n and line-based formats.
    """
    # First normalize multiple newlines
    raw_text = re.sub(r"\r\n", "\n", raw_text)
    
    # If the document has natural paragraph breaks, use them
    if "\n\n" in raw_text:
        return [b.strip() for b in raw_text.split("\n\n") if b.strip()]
    
    # Fallback: Group every 4-6 lines into a block if only single newlines exist
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
    chunk_size = 5
    return ["\n".join(lines[i:i + chunk_size]) for i in range(0, len(lines), chunk_size)]

def score_block(block: str) -> int:
    lower_block = block.lower()
    score = 0
    
    # Prioritize tables only if they have actual text
    if "[table" in lower_block or "|" in lower_block:
        score += 2
        
    for kw in RELEVANT_KEYWORDS:
        if kw in lower_block:
            score += 1
            
    return score

def trim_syllabus_text(raw_text: str, min_score: int = 1) -> str:
    blocks = split_into_blocks(raw_text)
    print(f"Total blocks detected: {len(blocks)}")
    retained_blocks = []
    
    for block in blocks:
        # Step A: Clean CID font artifacts
        cleaned_block, is_usable = clean_cid_artifacts(block)
        if not is_usable or not cleaned_block.strip():
            continue
            
        # Step B: Always keep top-level page indicators
        if cleaned_block.startswith("=== Page") and len(cleaned_block) < 30:
            retained_blocks.append(cleaned_block)
            continue
            
        # Step C: Score relevance
        if score_block(cleaned_block) >= min_score:
            retained_blocks.append(cleaned_block)
            
    return "\n\n".join(retained_blocks)

if __name__ == "__main__":
    with open("raw_output.txt", "r", encoding="utf-8") as f:
        raw_content = f.read()

    cleaned_content = trim_syllabus_text(raw_content)

    with open("cleaned_output.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_content)

    raw_len = len(raw_content)
    clean_len = len(cleaned_content)
    reduction = ((raw_len - clean_len) / raw_len) * 100

    print(f"Original length: {raw_len} chars")
    print(f"Cleaned length:  {clean_len} chars")
    print(f"Reduction:       {reduction:.1f}% noise removed")