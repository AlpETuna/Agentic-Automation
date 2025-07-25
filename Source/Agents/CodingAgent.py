from strands import Agent
import subprocess
import os
import tempfile
from datetime import datetime

class CodingAgent:
    def __init__(self):
        self.agent = Agent(
            name="coder",
            system_prompt="""You are a programming specialist for university computer science tasks.
            You write clean, well-documented code and can execute it to verify functionality.
            Always include proper error handling and follow best practices.
            Provide explanations for your code and suggest improvements."""
        )
    
    def write_code(self, task, language="python", requirements=None, output_dir="code"):
        # Generate main code
        main_prompt = f"""
        Write {language} code for: {task}
        {f"Requirements: {requirements}" if requirements else ""}
        
        Return ONLY the code with:
        - Proper imports
        - Well-commented functions
        - Error handling
        - No explanatory text
        """
        
        # Generate test cases
        test_prompt = f"""
        Write {language} test cases for: {task}
        
        Return ONLY test code with:
        - Import statements for testing
        - Multiple test functions
        - Edge cases and normal cases
        - No explanatory text
        """
        
        main_response = self.agent(main_prompt)
        test_response = self.agent(test_prompt)
        
        return self._save_and_test_code(str(main_response), str(test_response), language, task, output_dir)
    
    def _save_and_test_code(self, main_code, test_code, language, task, output_dir):
        extensions = {"python": ".py", "javascript": ".js", "java": ".java", "cpp": ".cpp"}
        ext = extensions.get(language, ".txt")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Clean and save main code
        clean_main = self._extract_code(main_code, language)
        main_filename = f"{output_dir}/main{ext}"
        
        with open(main_filename, 'w') as f:
            f.write(clean_main)
        
        # Clean and save test code
        clean_test = self._extract_code(test_code, language)
        test_filename = f"{output_dir}/test{ext}"
        
        with open(test_filename, 'w') as f:
            f.write(clean_test)
        
        # Test the main code
        test_result = self._execute_code(main_filename, language)
        
        return {
            "main_file": main_filename,
            "test_file": test_filename,
            "code": clean_main,
            "test_result": test_result
        }
    
    def _execute_code(self, file_path, language):
        try:
            if language == "python":
                result = subprocess.run(
                    ["python", file_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
            elif language == "javascript":
                result = subprocess.run(
                    ["node", file_path], 
                    capture_output=True, 
                    text=True, 
                    timeout=30
                )
            else:
                return {"status": "unsupported", "message": f"Execution not supported for {language}"}
            
            return {
                "status": "success" if result.returncode == 0 else "error",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "message": "Code execution timed out"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _extract_code(self, response_text, language):
        """Extract clean code from agent response"""
        lines = response_text.split('\n')
        code_lines = []
        in_code_block = False
        skip_explanatory = True
        
        for line in lines:
            # Skip explanatory text at start
            if skip_explanatory and not self._looks_like_code(line, language) and '```' not in line:
                continue
            skip_explanatory = False
            
            # Detect code block markers
            if '```' in line:
                in_code_block = not in_code_block
                continue
            
            # Skip explanatory text
            if self._is_explanatory_text(line):
                continue
                
            # Include lines that look like code
            if in_code_block or self._looks_like_code(line, language):
                code_lines.append(line)
        
        # Remove trailing explanatory text
        while code_lines and self._is_explanatory_text(code_lines[-1]):
            code_lines.pop()
            
        return '\n'.join(code_lines)
    
    def _looks_like_code(self, line, language):
        """Check if line looks like code"""
        line = line.strip()
        if not line or line.startswith('#'):
            return True
        
        if language == "python":
            python_keywords = ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ', 'try:', 'except:', 'return ', 'print(']
            return any(line.startswith(kw) for kw in python_keywords) or '=' in line or line.endswith(':')
        
        return False
    
    def _is_explanatory_text(self, line):
        """Check if line is explanatory text to remove"""
        line = line.strip().lower()
        explanatory_phrases = [
            'here is', 'here\'s', 'this code', 'the code', 'above code',
            'this implementation', 'this function', 'explanation:', 'note:',
            'this will', 'you can', 'let me', 'i\'ve', 'as you can see'
        ]
        return any(phrase in line for phrase in explanatory_phrases) and len(line) > 10