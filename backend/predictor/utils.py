

def safe_float(val):
   try:
       return float(str(val).replace("%", "").strip())
   except Exception:
       return None


def safe_int(val):
   try:
       return int(val)
   except Exception:
       return None


def clamp(value, low=0.0, high=100.0):
   return max(low, min(high, float(value)))


def normalize_weights(weights):
   total = sum(weights.values())
   if total <= 0:
       return weights
   return {k: (v * 100.0 / total) for k, v in weights.items()}


