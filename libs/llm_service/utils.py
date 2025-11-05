import json
import re
import ast

def parse_llm_json_response(response: str) -> dict:
    """
    Parse the 'response' field that contains JSON wrapped in markdown fences.
    
    Example input:
    ```json
    {
      "is_sensitive": false,
      "matched_topics": [],
      "reason": "Some text"
    }
    ```
    
    Returns:
        dict: Parsed JSON object.
    """
    # Remove markdown fences like ```json ... ```
    cleaned = re.sub(r"^```json\s*|\s*```$", "", response.strip(), flags=re.DOTALL)
    print('################## parse_llm_json_response ##################')
    print(f'{cleaned=}')

    # Parse into Python dict
    return json.loads(cleaned)


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flattens a nested dictionary, joining keys with `sep`.
    
    Example:
        {'a': 5, 'b': {'c': {'d': 3}, 'e': 3}}
        -> {'a': 5, 'b.c.d': 3, 'b.e': 3}
    """
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items



def safe_literal_eval(value):
    """
    Try to safely evaluate a Python literal from a string.
    If parsing fails (e.g., it's not valid Python literal syntax),
    return the original value unchanged.
    """
    if not isinstance(value, str):
        return value  # only try to eval strings

    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return value
