import math


def calculate(expression: str) -> str:
    """Safely evaluates a basic mathematical expression.
    
    Supports +, -, *, /, **, %, sqrt, sin, cos, tan, log, exp.
    """
    safe_dict = {
        "__builtins__": None,
        "math": math,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
    }
    # Sanitize characters to avoid arbitrary code execution
    cleaned = expression.strip()
    if any(c in cleaned for c in [";", "\n", "import", "exec", "eval", "__", "lambda"]):
        return "Error: Unsupported or unsafe characters in arithmetic expression."
    
    try:
        result = eval(cleaned, safe_dict)
        return str(result)
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e!s}"
