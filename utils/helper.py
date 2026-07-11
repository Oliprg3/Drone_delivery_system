from typing import List, Any

def flatten(lst: List[List[Any]]) -> List[Any]:
    return [item for sublist in lst for item in sublist]
