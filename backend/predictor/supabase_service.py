import os
from supabase import create_client, Client


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")




def get_supabase() -> Client:
   """Safely create client only when needed (not at module import)."""
   if not SUPABASE_URL or not SUPABASE_KEY:
       raise Exception("Supabase credentials missing. Check .env values.")
   return create_client(SUPABASE_URL, SUPABASE_KEY)




def log_prediction_to_db(payload: dict):
   try:
       supabase = get_supabase()


       supabase.table("prediction").insert({
           "professor_id": payload.get("professor_id"),
           "course_name": payload.get("course_name"),
           "final_score": payload.get("final_score"),
           "margin_of_error": payload.get("margin_of_error"),
           "predicted_range": payload.get("predicted_range"),
           "rmp_difficulty": payload.get("rmp_difficulty"),
           "rmp_wta": payload.get("rmp_wta"),
           "rmp_reliability": payload.get("rmp_reliability"),
       }).execute()


   except Exception as e:
       print("Supabase logging failed:", e)