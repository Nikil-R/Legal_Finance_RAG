import re
from pathlib import Path


def sanitize_filename(filename: str) -> str:
    # 1. Strip directories
    safe = Path(filename).name
    
    # 2. Remove special characters (keep alphanum, underscore, hyphen, dot)
    safe = re.sub(r'[^\w\-.]', '_', safe)
    
    # 3. Block hidden files and parent directory references
    if '..' in safe or safe.startswith('.'):
        raise ValueError("Invalid filename")
        
    return safe

# Test cases
test_cases = [
    "normal.pdf",
    "../../../etc/passwd",
    "some/dir/file.txt",
    ".hidden",
    "file..name",
    "space name.docx",
    "malicious\x00filename.txt"
]

for tc in test_cases:
    print(f"Testing: {tc}")
    try:
        sanitized = sanitize_filename(tc)
        print(f"  Result: {sanitized}")
    except ValueError as e:
        print(f"  Caught expected error: {e}")
    except Exception as e:
        print(f"  Caught unexpected error: {type(e).__name__}: {e}")
