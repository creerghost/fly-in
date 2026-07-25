#!/usr/bin/env python3
import subprocess
import sys
import os
import re
from google import genai

def run_linter():
    print("Running make lint...")
    result = subprocess.run(
        ["make", "lint"],
        capture_output=True,
        text=True
    )
    return result.returncode, result.stdout, result.stderr

def extract_files_with_errors(lint_output):
    # Match patterns like: path/to/file.py:line:col or path/to/file.py:line: error
    files = set()
    for line in lint_output.splitlines():
        match = re.match(r'^([a-zA-Z0-9_/\.\-]+):[0-9]+:', line)
        if match:
            files.add(match.group(1))
    return list(files)

def fix_file_with_gemini(client, file_path, lint_output):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, "r") as f:
        original_code = f.read()

    prompt = f"""You are an expert Python developer.
The following file `{file_path}` has some linting/type-checking errors.
Here is the output from `make lint`:

{lint_output}

Here is the original code for `{file_path}`:

```python
{original_code}
```

Please provide the completely fixed code for `{file_path}`.
Output ONLY the raw valid Python code without any markdown formatting, backticks, or explanations. Do not include ```python or ``` at the end. Just the code.
"""

    print(f"Asking Gemini to fix {file_path}...")
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=prompt,
    )
    
    fixed_code = response.text
    # Cleanup in case the model ignored instructions and included markdown
    if fixed_code.startswith("```python\n"):
        fixed_code = fixed_code[10:]
    if fixed_code.endswith("\n```"):
        fixed_code = fixed_code[:-4]
    if fixed_code.endswith("```"):
        fixed_code = fixed_code[:-3]
        
    with open(file_path, "w") as f:
        f.write(fixed_code)
    print(f"Successfully applied fixes to {file_path}")

def main():
    returncode, stdout, stderr = run_linter()
    lint_output = stdout + "\n" + stderr
    
    if returncode == 0:
        print("Linting passed! No fixes needed.")
        sys.exit(0)
        
    print("Linting failed. Identifying files with errors...")
    files_to_fix = extract_files_with_errors(lint_output)
    
    if not files_to_fix:
        print("Could not identify specific files to fix from the lint output.")
        print(lint_output)
        sys.exit(1)
        
    print(f"Found errors in files: {', '.join(files_to_fix)}")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable is missing.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    for file_path in files_to_fix:
        fix_file_with_gemini(client, file_path, lint_output)
        
    print("All fixes applied. Re-running linter to verify...")
    final_returncode, final_stdout, final_stderr = run_linter()
    
    if final_returncode == 0:
        print("Success! The AI correctly fixed all linting errors.")
        sys.exit(0)
    else:
        print("The AI attempted to fix the errors, but some issues remain:")
        print(final_stdout + "\n" + final_stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
