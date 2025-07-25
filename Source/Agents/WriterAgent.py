from strands import Agent
import os
from datetime import datetime
import subprocess

class WriterAgent:
    def __init__(self):
        self.agent = Agent(
            name="writer",
            system_prompt="""You are an academic writing specialist for university students. 
            You excel at creating well-structured reports, essays, and documentation.
            Always structure your output with clear sections and ensure proper academic formatting:
            - Clear abstract, introduction, main content, and conclusion
            - Proper citations and references
            - Academic tone and language
            - Logical flow and coherent arguments"""
        )
    
    def write_report(self, topic, requirements, sources=None, create_pdf=False, template="academic"):
        prompt = f"""
        Write an academic report on: {topic}
        
        Requirements: {requirements}
        
        {f"Available sources: {sources}" if sources else ""}
        
        Structure your response with these sections:
        - ABSTRACT: Brief summary (2-3 sentences)
        - INTRODUCTION: Context and objectives
        - CONTENT: Main body with detailed analysis
        - CONCLUSION: Key findings and implications
        
        Write in academic style with clear, structured content.
        """
        
        response = self.agent(prompt)
        return self._save_document(str(response), topic, create_pdf, template)
    
    def _save_document(self, content, title, create_pdf=False, template="academic"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{title.replace(' ', '_')}_{timestamp}"
        
        os.makedirs("reports", exist_ok=True)
        
        # Generate LaTeX content
        latex_content = self._generate_latex(content, title, template)
        latex_path = f"reports/{filename}.tex"
        
        with open(latex_path, 'w') as f:
            f.write(latex_content)
        
        result = {"latex": latex_path}
        
        # Create PDF only if requested
        if create_pdf:
            pdf_path = self._compile_latex(latex_path)
            if pdf_path:
                result["pdf"] = pdf_path
        
        return result
    
    def _generate_latex(self, content, title, template):
        """Generate LaTeX document from content using template"""
        template_path = f"Agentic-Automation/templates/{template}_report.tex"
        
        if not os.path.exists(template_path):
            template_path = "Agentic-Automation/templates/academic_report.tex"
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Parse content sections
        sections = self._parse_content_sections(content)
        
        # Replace template placeholders
        latex_content = template_content.replace("{{TITLE}}", title)
        latex_content = latex_content.replace("{{AUTHOR}}", "Student")
        latex_content = latex_content.replace("{{DATE}}", datetime.now().strftime("%B %d, %Y"))
        latex_content = latex_content.replace("{{ABSTRACT}}", sections.get("abstract", "Abstract content"))
        latex_content = latex_content.replace("{{INTRODUCTION}}", sections.get("introduction", "Introduction content"))
        latex_content = latex_content.replace("{{CONTENT}}", sections.get("content", content))
        latex_content = latex_content.replace("{{CONCLUSION}}", sections.get("conclusion", "Conclusion content"))
        
        return latex_content
    
    def _parse_content_sections(self, content):
        """Parse content into sections"""
        sections = {}
        current_section = None
        current_content = []
        
        for line in content.split('\n'):
            line = line.strip()
            if any(keyword in line.lower() for keyword in ['abstract', 'introduction', 'conclusion']):
                if current_section:
                    sections[current_section] = '\n'.join(current_content)
                
                if 'abstract' in line.lower():
                    current_section = 'abstract'
                elif 'introduction' in line.lower():
                    current_section = 'introduction'
                elif 'conclusion' in line.lower():
                    current_section = 'conclusion'
                
                current_content = []
            else:
                current_content.append(line)
        
        if current_section:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _compile_latex(self, latex_path):
        """Compile LaTeX to PDF"""
        try:
            # Change to reports directory for compilation
            reports_dir = os.path.dirname(latex_path)
            tex_file = os.path.basename(latex_path)
            
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_file],
                capture_output=True,
                text=True,
                cwd=reports_dir
            )
            
            pdf_path = latex_path.replace(".tex", ".pdf")
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                return pdf_path
            else:
                print(f"LaTeX compilation failed. Trying alternative method...")
                # Try with pandoc as fallback
                return self._pandoc_fallback(latex_path)
        except FileNotFoundError:
            print("pdflatex not found. Trying pandoc fallback...")
            return self._pandoc_fallback(latex_path)
    
    def _pandoc_fallback(self, latex_path):
        """Fallback PDF generation using pandoc"""
        try:
            pdf_path = latex_path.replace(".tex", ".pdf")
            result = subprocess.run(
                ["pandoc", latex_path, "-o", pdf_path],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists(pdf_path):
                return pdf_path
            else:
                print("PDF generation failed. LaTeX file saved for manual compilation.")
                return None
        except FileNotFoundError:
            print("Neither pdflatex nor pandoc found. LaTeX file saved for manual compilation.")
            return None