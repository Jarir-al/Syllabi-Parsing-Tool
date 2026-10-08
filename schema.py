from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class ItemType(str, Enum):
    HOMEWORK = "homework"
    EXAM = "exam"
    QUIZ = "quiz"
    PROJECT = "project"
    LAB = "lab"
    READING = "reading"
    OTHER = "other"

class Deliverable(BaseModel):
    title: str = Field(description="Name or title of the assignment, exam, or deliverable")
    type: ItemType = Field(description="Classification of the deliverable")
    due_date: Optional[str] = Field(
        None, 
        description="ISO date string (YYYY-MM-DD) if determinable, or the explicit relative schedule string"
    )
    date_notes: Optional[str] = Field(
        None,
        description="Brief note on how the date was resolved if relative (e.g., 'Assigned Mon Oct 12; due next Wed Oct 21')"
    )
    raw_points: Optional[str] = Field(
        None, 
        description="The points stated in the syllabus, e.g., '100 pts', '150/1300', or None if expressed only as %"
    )
    weight_percentage: Optional[float] = Field(
        None, 
        description="Normalized weight between 0.0 and 1.0 (e.g., 0.15 for 15%). Null if unknown."
    )

class GradeCategory(BaseModel):
    category_name: str = Field(description="Name of category, e.g., 'Exams', 'Homework', 'Quizzes'")
    raw_weight_or_points: str = Field(description="As written in syllabus, e.g., '400 / 1300 pts' or '30%'")
    normalized_percentage: float = Field(
        description="Decimal percentage between 0.0 and 1.0 representing the category's share of the final grade"
    )

class GradeCutoff(BaseModel):
    letter: str = Field(description="Letter grade, e.g., 'A+', 'A', 'A-', 'B+'")
    min_score: float = Field(description="Minimum percentage or point cutoff, e.g., 97.0 or 0.97")
    max_score: Optional[float] = Field(None, description="Maximum boundary if specified, e.g., 100.0")
    raw_range: Optional[str] = Field(None, description="Verbatim range from syllabus, e.g., '97 - 100' or '>= 93%'")

class CourseSyllabus(BaseModel):
    course_code: str = Field(description="Course code/number, e.g., 'CS 3345' or 'ARCH 4301'")
    course_title: str = Field(description="Full name of the course")
    instructor: Optional[str] = Field(None, description="Primary instructor name")
    office_hours: Optional[str] = Field(None, description="Instructor office hours and times/location")
    location: Optional[str] = Field(None, description="Classroom location or meeting mode (e.g., 'ECSS 2.410' or 'Online')")
    
    total_course_points: Optional[str] = Field(
        None, 
        description="Total points possible in course if point-based, e.g., '1300 points' or '100%'"
    )
    grade_distribution: List[GradeCategory] = Field(
        default_factory=list, 
        description="Breakdown of grading weights/categories"
    )
    letter_grade_scale: List[GradeCutoff] = Field(
        default_factory=list,
        description="Letter grade cutoffs/scale if provided in syllabus (e.g., A+ = 97-100, A = 93-96.9)"
    )
    deliverables: List[Deliverable] = Field(
        default_factory=list, 
        description="All homework assignments, exams, quizzes, and project deadlines found in the syllabus"
    )