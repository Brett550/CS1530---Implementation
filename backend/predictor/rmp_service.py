import RateMyProfessor_Database_APIs
from .utils import safe_float, safe_int


def get_professor_info(professor_id: int):
   try:
       prof = RateMyProfessor_Database_APIs.fetch_a_professor(professor_id)
       return {
           "name": f"{prof.first_name} {prof.last_name}",
           "avg_rating": safe_float(prof.avg_rating),
           "avg_difficulty": safe_float(prof.avg_difficulty),
           "num_ratings": safe_int(prof.num_ratings),
           "would_take_again_percent": safe_float(prof.would_take_again_percent),
       }
   except Exception as e:
       return {"error": str(e)}