from typing import List, Dict


# Estratégias de avaliação em memória sobre "últimos N valores"


def eval_abs_range(value: float, min_v: float | None, max_v: float | None) -> bool:
 if min_v is not None and value < min_v:
  return True
 if max_v is not None and value > max_v:
  return True
 return False


def eval_moving_mean_std(values: List[float], k_std: float) -> Dict[str, float] | None:
# Retorna dict com mean/std/last/outlier: bool
 if not values:
  return None
 import math
 n = len(values)
 mean = sum(values) / n
 var = sum((x - mean) ** 2 for x in values) / max(1, n - 1)
 std = math.sqrt(var)
 last = values[-1]
 outlier = abs(last - mean) > k_std * std if std > 0 else False
 return {"mean": mean, "std": std, "last": last, "outlier": outlier}
