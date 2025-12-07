from rest_framework.decorators import api_view
from rest_framework.response import Response
from .supabase_service import log_prediction_to_db


from .canvas_service import (
   fetch_courses,
   fetch_all_data,
   fetch_category_grades,
   load_cache_if_exists
)


from .rmp_service import get_professor_info
from .ai_service import compute_strengths, compute_prediction, compute_advice




# ------------------ Health ------------------
@api_view(["GET"])
def health_check(_request):
   return Response({"status": "ok"})




# ------------------ Canvas ------------------
@api_view(["GET"])
def get_canvas_courses(_request):
   return Response(fetch_courses())




@api_view(["GET"])
def get_canvas_all_data(_request):
   return Response(fetch_all_data())




@api_view(["GET"])
def get_canvas_category_grades(_request, course_id: int):
   return Response(fetch_category_grades(course_id))




# ------------------ Predict Grade ------------------
@api_view(["POST"])
def predict_grade(request):
   professor_id = request.data.get("professor_id")
   syllabus_text = (request.data.get("syllabus_text") or "").strip()
   canvas_course_id = request.data.get("canvas_course_id")


   # load cached historical Canvas data
   df = load_cache_if_exists()
   if df is None:
       return Response({"error": "No Canvas data cache found. Run /canvas/all-data first."}, status=400)


   # compute average category strengths from history
   category_means = {}
   for cat in ["projects", "assignments", "exams", "participation"]:
       if cat in df.columns:
           valid = df[cat].dropna()
           category_means[cat] = float(valid.mean()) if not valid.empty else None
       else:
           category_means[cat] = None


   # calculate fallback overall
   non_null_vals = [v for v in category_means.values() if v is not None]
   default_overall = float(sum(non_null_vals) / len(non_null_vals)) if non_null_vals else 85.0


   # AI: finalize strengths (with fallback)
   strengths = compute_strengths(category_means, default_overall)


   # RMP enrichment
   rmp_pack = get_professor_info(int(professor_id)) if professor_id else None


   # AI: produce weights + final grade + margin + range
   final = compute_prediction(strengths, syllabus_text, rmp_pack)


   # resolve course name (optional)
   course_name = None
   try:
       if canvas_course_id:
           row = df[df["course_id"] == int(canvas_course_id)]
           if not row.empty:
               course_name = str(row.iloc[0]["name"])
   except:
       course_name = None


   # AI: produce long-form advice
   advice_text = compute_advice(final, strengths, course_name, rmp_pack)
   log_prediction_to_db({
       "professor_id": professor_id,
       "course_name": course_name,
       "final_score": final.get("final_score"),
       "margin_of_error": final.get("margin_of_error"),    # updated
       "predicted_range": final.get("range"),              # updated
       "rmp_difficulty": rmp_pack.get("avg_difficulty") if rmp_pack else None,
       "rmp_wta": rmp_pack.get("would_take_again_percent") if rmp_pack else None,
       "rmp_reliability": rmp_pack.get("reliability") if rmp_pack else None,
   })


  
   return Response({
       "course_name": course_name,
       "category_strengths": strengths.get("category_strengths"),
       "overall_strength": strengths.get("overall_strength"),
       "punctual_strength": strengths.get("punctual_strength"),
       "final_score": final.get("final_score"),
       "margin_of_error": final.get("margin_of_error"),
       "range": final.get("range"),
       "projects": final.get("projects"),
       "assignments": final.get("assignments"),
       "exams": final.get("exams"),
       "participation": final.get("participation"),
       "rmp": rmp_pack,
       "advice": advice_text
   })


  






# ------------------ Explanation Only ------------------
@api_view(["POST"])
def explain_prediction(request):
   course = request.data.get("course")
   grade = request.data.get("predicted_grade")
   factors = request.data.get("factors", [])
   professor_id = request.data.get("professor_id")


   prompt = f"""
   A student is considering {course}.
   Their predicted grade is {grade}.
   Factors influencing this: {', '.join(factors)}.


   Write a short explanation (2-3 sentences) plus a bulleted list of 3 main reasons.
   """


   from openai import OpenAI
   client = OpenAI()


   completion = client.chat.completions.create(
       model="gpt-4o-mini",
       messages=[{"role": "user", "content": prompt}],
       max_tokens=140,
   )
   explanation = completion.choices[0].message.content.strip()


   professor_info = get_professor_info(professor_id) if professor_id else None


   return Response({
       "explanation": explanation,
       "professor": professor_info
   })


@api_view(["GET"])
def get_prediction_history(_request):
   result = supabase.table("predictions").select("*").order("timestamp", desc=True).execute()
   return Response(result.data)
