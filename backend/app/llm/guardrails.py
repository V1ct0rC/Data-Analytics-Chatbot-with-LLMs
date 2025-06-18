"""
Content moderation and safety controls for LLM interactions. This module implements a template for moderating
LLM interactions. It only covers basic content moderation and SQL query validation.
"""
import re
from typing import Dict, Any, Tuple, List


BANNED_PATTERNS = [
    r'(?i)(hack|crack|steal|illegal|exploit)',
    r'(?i)(personal data|credit card|social security)',
    r'(?i)(hate speech|racial slur|offensive)'
]

def validate_user_prompt(prompt: str) -> bool:
    """
    Check if the prompt contains inappropriate content.
    
    Args:
        prompt: The user input to check
        
    Returns:
        Tuple of (is_safe, message)
    """
    for pattern in BANNED_PATTERNS:
        if re.search(pattern, prompt):
            return False
    
    return True

def moderate_response(response: str) -> str:
    """
    Filter out potentially harmful content from responses.
    
    Args:
        response: The LLM response to filter
        
    Returns:
        Filtered response
    """
    # TODO: Replace with more sophisticated filtering
    for pattern in BANNED_PATTERNS:
        response = re.sub(pattern, "[filtered]", response, flags=re.IGNORECASE)
    
    return response


ALLOWED_TABLES = ["clientes"]

def validate_table_access(sql_query: str) -> Tuple[bool, str]:
    """
    Validate that the query only accesses allowed tables.
    
    Args:
        sql_query: The SQL query to validate
        
    Returns:
        Tuple of (is_allowed, message)
    """
    tables_in_query = re.findall(r'(?i)from\s+([a-z0-9_]+)', sql_query)
    tables_in_query += re.findall(r'(?i)join\s+([a-z0-9_]+)', sql_query)
    
    for table in tables_in_query:
        if table.lower() not in ALLOWED_TABLES:
            return False, f"Access to table '{table}' is not allowed."
    
    return True, ""


if __name__ == "__main__":
    prompt = "Can you hack into the database?"
    is_safe = validate_user_prompt(prompt)
    print(f"Prompt moderation: {is_safe}, Message: {prompt}")
    
    response = "Here is some personal data."
    filtered_response = moderate_response(response)
    print(f"Filtered response: {filtered_response}")
    
    sql_query = "SELECT * FROM vendas JOIN clientes ON vendas.cliente_id = clientes.id"
    is_allowed, access_message = validate_table_access(sql_query)
    print(f"Table access validation: {is_allowed}, Message: {access_message}")