import json
import re

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

    # Parse into Python dict
    return json.loads(cleaned)



def clean_cypher_query(query: str) -> str:
    """
    Clean a generated Cypher query by removing escape characters and normalizing whitespace.
    """
    # Remove \n, \t, and \r
    cleaned = query.replace("\\n", " ").replace("\\t", " ").replace("\\r", " ")

    # Collapse multiple spaces into one
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Strip leading/trailing spaces
    return cleaned.strip()


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