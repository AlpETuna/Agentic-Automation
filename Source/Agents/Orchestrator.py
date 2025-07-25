from strands import Agent
from strands.multiagent import Swarm
from .WriterAgent import WriterAgent
from .CodingAgent import CodingAgent
from .GitAgent import GitAgent
from .RAGAgent import RAGAgent
from .ResearchAgent import ResearchAgent
import json

class UniversityOrchestrator:
    def __init__(self, aws_region="us-east-1", repo_path="."):
        # Initialize specialized agents
        self.writer = WriterAgent()
        self.coder = CodingAgent()
        self.git_manager = GitAgent(repo_path)
        self.rag = RAGAgent(aws_region)
        self.researcher = ResearchAgent()
        
        # Create coordination agent
        self.coordinator = Agent(
            name="coordinator",
            system_prompt="""You are a university task coordinator. You analyze student requests
            and determine which specialized agents should handle different parts of the task.
            You can delegate to: writer (reports/essays), coder (programming), git_manager (version control),
            and rag (knowledge retrieval). Coordinate complex multi-step academic workflows."""
        )
        
        # Create swarm for complex tasks
        self.swarm = Swarm(
            [self.coordinator, self.writer.agent, self.coder.agent, self.git_manager.agent, self.rag.agent, self.researcher.agent],
            max_handoffs=15,
            max_iterations=15
        )
    
    def handle_request(self, request, context=None):
        """Main entry point for handling university tasks"""
        
        # First, check if we need knowledge retrieval
        if self._needs_knowledge_retrieval(request):
            knowledge = self.rag.query_knowledge_base(request)
            if knowledge["status"] == "success" and knowledge["answer"]:
                context = knowledge["answer"]
            else:
                # If no relevant info in RAG, use research agent
                print("🔍 No relevant information found in knowledge base. Researching...")
                research = self.researcher.research_topic(request)
                if research["status"] == "success":
                    context = research["findings"]
        
        # Determine task type and route accordingly
        task_type = self._classify_task(request)
        
        if task_type == "writing":
            return self._handle_writing_task(request, context)
        elif task_type == "coding":
            return self._handle_coding_task(request, context)
        elif task_type == "git":
            return self._handle_git_task(request)
        elif task_type == "complex":
            return self._handle_complex_task(request, context)
        else:
            return {"status": "error", "message": "Could not classify task"}
    
    def _classify_task(self, request):
        """Classify the type of task"""
        request_lower = request.lower()
        
        if any(word in request_lower for word in ["write", "report", "essay", "document"]):
            return "writing"
        elif any(word in request_lower for word in ["code", "program", "implement", "debug"]):
            return "coding"
        elif any(word in request_lower for word in ["commit", "push", "git", "repository"]):
            return "git"
        else:
            return "complex"
    
    def _needs_knowledge_retrieval(self, request):
        """Check if request needs knowledge base lookup"""
        keywords = ["rubric", "course", "assignment", "notes", "material", "reference"]
        return any(keyword in request.lower() for keyword in keywords)
    
    def _handle_writing_task(self, request, context=None):
        """Handle writing-focused tasks"""
        # Extract topic and requirements
        prompt = f"Extract the topic and requirements from this request: {request}"
        if context:
            prompt += f"\nAdditional context: {context}"
        
        analysis = self.coordinator(prompt)
        
        # Always create PDF for reports
        result = self.writer.write_report(
            topic=request,
            requirements=str(analysis),
            sources=context,
            create_pdf=True
        )
        
        # Auto-commit if successful
        if result:
            self.git_manager.commit_changes([result["markdown"]], f"Add report: {request}")
        
        return result
    
    def _handle_coding_task(self, request, context=None):
        """Handle coding-focused tasks"""
        # Extract output directory if specified, otherwise use task-based folder
        output_dir = None
        if "output to" in request.lower() or "save to" in request.lower():
            words = request.split()
            for i, word in enumerate(words):
                if word.lower() in ["to", "in"] and i + 1 < len(words):
                    output_dir = words[i + 1]
                    break
        
        if not output_dir:
            # Create folder based on task name
            task_name = request.replace("write", "").replace("code", "").replace("implementation", "").strip()
            output_dir = f"code/{task_name.replace(' ', '_').lower()}"
        
        result = self.coder.write_code(
            task=request,
            requirements=context,
            output_dir=output_dir
        )
        
        # Auto-commit if code runs successfully
        if result["test_result"]["status"] == "success":
            files_to_commit = [result["main_file"], result["test_file"]]
            self.git_manager.commit_changes(files_to_commit, f"Add working code: {request}")
        
        return result
    
    def _handle_git_task(self, request):
        """Handle Git operations"""
        if "commit" in request.lower():
            return self.git_manager.commit_changes(["*"], request)
        elif "push" in request.lower():
            return self.git_manager.push_to_remote()
        else:
            return {"status": "error", "message": "Git operation not recognized"}
    
    def _handle_complex_task(self, request, context=None):
        """Handle complex multi-agent tasks using swarm"""
        enhanced_request = request
        if context:
            enhanced_request += f"\n\nContext from knowledge base: {context}"
        
        result = self.swarm(enhanced_request)
        return {
            "status": result.status,
            "result": str(result),
            "agents_used": [node.node_id for node in result.node_history]
        }