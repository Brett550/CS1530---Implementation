import os
import pandas as pd
import requests
from pathlib import Path


CACHE_PATH = Path("canvas_data_cache.csv")


CANVAS_API_URL = os.getenv("CANVAS_API_URL", "https://canvas.pitt.edu/api/v1")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
headers = {"Authorization": f"Bearer {CANVAS_TOKEN}"}




# ------------------ Fetch All Courses ------------------
def fetch_courses():
   url = f"{CANVAS_API_URL}/courses"
   response = requests.get(url, headers=headers)
   return response.json()




# ------------------ Fetch Category Grades for 1 Course ------------------
def fetch_category_grades(course_id: int):
   # identical to old get_canvas_category_grades response logic
   course_url = f"{CANVAS_API_URL}/courses/{course_id}"
   course_info = requests.get(course_url, headers=headers).json()


   groups = requests.get(
       f"{CANVAS_API_URL}/courses/{course_id}/assignment_groups",
       headers=headers,
       params={"include[]": "assignments"},
   ).json()


   submissions = requests.get(
       f"{CANVAS_API_URL}/courses/{course_id}/students/submissions",
       headers=headers,
       params={"student_ids[]": "self"},
   ).json()


   submission_map = {s.get("assignment_id"): s for s in submissions if isinstance(s, dict)}


   results = []
   
   for g in groups:
       total_points, earned_points = 0, 0
       assignments_list = []


       for a in g.get("assignments", []):
           assignment_id = a["id"]
           points_possible = a.get("points_possible") or 0
           submission = submission_map.get(assignment_id)
           score = submission.get("score") if submission else None


           if score is not None and points_possible > 0:
               earned_points += score
               total_points += points_possible


           assignments_list.append({
               "id": assignment_id,
               "name": a.get("name"),
               "points_possible": points_possible,
               "score": score,
               "html_url": a.get("html_url"),
           })


       percent = (earned_points / total_points * 100) if total_points > 0 else None


       results.append({
           "category": g["name"],
           "weight": g.get("group_weight"),
           "earned_points": earned_points,
           "total_points": total_points,
           "percent": percent,
           "assignments": assignments_list
       })


   return {
       "course": {
           "id": course_info.get("id"),
           "name": course_info.get("name"),
           "course_code": course_info.get("course_code"),
       },
       "categories": results
   }
   
   # ------------------ Fetch ALL Canvas Data & Cache ------------------
def fetch_all_data():
   courses_url = f"{CANVAS_API_URL}/courses"
   params = {
       "enrollment_state[]": ["active", "completed", "invited_or_pending"],
       "per_page": 100,
       "include[]": ["term"],
   }


   courses = requests.get(courses_url, headers=headers, params=params).json()


   all_data, csv_rows = [], []


   def standardize_category(name: str) -> str:
       n = (name or "").lower()
       if any(k in n for k in ["exam", "midterm", "final", "quiz", "test"]): return "exams"
       if any(k in n for k in ["project", "capstone", "lab"]): return "projects"
       if any(k in n for k in ["participation","attendance","discussion","poll","peer"]): return "participation"
       return "assignments"


   for course in courses:
       try:
           cid = course.get("id")
           if not cid:
               continue


           detail_url = f"{CANVAS_API_URL}/courses/{cid}"
           detail = requests.get(detail_url, headers=headers).json()
           term = (course.get("term") or {}).get("name", "")


           enrollments = requests.get(
               f"{CANVAS_API_URL}/courses/{cid}/enrollments",
               headers=headers,
               params={"user_id": "self", "type[]": "StudentEnrollment"},
           ).json()


           grades = enrollments[0].get("grades", {}) if isinstance(enrollments, list) and enrollments else {}
           final_grade = grades.get("final_grade") or grades.get("current_grade")
