import logging
import os
from dotenv import load_dotenv
from Agents.Orchestrator import UniversityOrchestrator

# Load environment variables
load_dotenv()

# Enable debug logs
logging.getLogger("strands.multiagent").setLevel(logging.DEBUG)
logging.basicConfig(
    format="%(levelname)s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler()]
)

def main():
    # Initialize the university automation system
    orchestrator = UniversityOrchestrator(
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        repo_path=os.getenv("REPO_PATH", ".")
    )
    
    print("🎓 University Automation System Ready!")
    print("Available commands:")
    print("- Write reports/essays")
    print("- Code and test programs") 
    print("- Manage Git repositories")
    print("- Query course materials")
    print("- Upload notes and documents")
    print("- Complex multi-step tasks")
    print("\nSpecial commands:")
    print("/upload <file> [type] - Upload document to knowledge base")
    print("/bulk - Run bulk upload helper")
    print("/run <file> - Execute a generated code file")
    print("\nType 'quit' to exit\n")
    
    while True:
        try:
            user_input = input("📚 What can I help you with? ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            # Handle special commands
            if user_input.startswith("/upload"):
                handle_upload(orchestrator, user_input)
                continue
            
            if user_input.startswith("/bulk"):
                import subprocess
                subprocess.run(["python", "../upload_helper.py"])
                continue
            
            if user_input.startswith("/run"):
                handle_run_code(user_input)
                continue
            
            # Process the request
            result = orchestrator.handle_request(user_input)
            
            # Display results
            if isinstance(result, dict):
                if result.get("status") == "success":
                    print("✅ Task completed successfully!")
                    if "main_file" in result:
                        print(f"📄 Main code saved to: {result['main_file']}")
                        print(f"🧪 Test code saved to: {result['test_file']}")
                    if "file_path" in result:
                        print(f"📄 Output saved to: {result['file_path']}")
                    if "latex" in result:
                        print(f"📝 LaTeX report saved as: {result['latex']}")
                    if "pdf" in result:
                        print(f"📄 PDF compiled as: {result['pdf']}")
                    if "test_result" in result:
                        print(f"🧪 Code test: {result['test_result']['status']}")
                else:
                    print(f"❌ Error: {result.get('message', 'Unknown error')}")
            else:
                print(f"📋 Result: {result}")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")

def handle_run_code(command):
    """Handle code execution commands"""
    parts = command.split()
    if len(parts) < 2:
        print("Usage: /run <file_path>")
        print("Example: /run code/binary_search_20250724_222606.py")
        return
    
    file_path = parts[1]
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"🚀 Executing {file_path}...")
    try:
        import subprocess
        result = subprocess.run(["python", file_path], capture_output=True, text=True)
        
        if result.stdout:
            print("📤 Output:")
            print(result.stdout)
        
        if result.stderr:
            print("❌ Errors:")
            print(result.stderr)
            
        print(f"✅ Execution completed with exit code: {result.returncode}")
        
    except Exception as e:
        print(f"❌ Execution failed: {str(e)}")

def handle_upload(orchestrator, command):
    """Handle document upload commands"""
    parts = command.split()
    if len(parts) < 2:
        print("Usage: /upload <file_path> [type]")
        print("Types: notes, rubric, course_material, assignment")
        print("Example: /upload my_notes.txt notes")
        return
    
    file_path = parts[1]
    doc_type = parts[2] if len(parts) > 2 else "notes"
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    print(f"📤 Uploading {file_path} as {doc_type}...")
    result = orchestrator.rag.upload_document(file_path, doc_type)
    
    if result["status"] == "success":
        print(f"✅ Document uploaded and indexed: {file_path}")
        print(f"📁 Stored as: {doc_type}")
    else:
        print(f"❌ Upload failed: {result['message']}")

if __name__ == "__main__":
    main()