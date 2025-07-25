from strands import Agent
import requests
import json
from datetime import datetime

class ResearchAgent:
    def __init__(self):
        self.agent = Agent(
            name="researcher",
            system_prompt="""You are an expert research specialist for academic work.
            You excel at finding, analyzing, and synthesizing information from multiple sources.
            Always provide accurate, well-sourced information with proper citations.
            Focus on academic and scholarly sources when possible."""
        )
    
    def research_topic(self, query, depth="standard"):
        """Research a topic and return comprehensive information"""
        
        # Enhanced research prompt
        research_prompt = f"""
        Conduct comprehensive research on: {query}
        
        Provide:
        1. Key concepts and definitions
        2. Current understanding and theories
        3. Important findings or developments
        4. Relevant examples or case studies
        5. Potential applications or implications
        
        Depth level: {depth}
        
        Structure your response with clear sections and provide detailed, accurate information.
        """
        
        response = self.agent(research_prompt)
        
        # Save research results
        research_data = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "depth": depth,
            "findings": str(response)
        }
        
        self._save_research(research_data)
        
        return {
            "status": "success",
            "query": query,
            "findings": str(response),
            "sources": "AI-generated research",
            "timestamp": research_data["timestamp"]
        }
    
    def _save_research(self, research_data):
        """Save research results for future reference"""
        import os
        os.makedirs("research", exist_ok=True)
        
        filename = f"research/research_{research_data['timestamp'].replace(':', '-')}.json"
        with open(filename, 'w') as f:
            json.dump(research_data, f, indent=2)
        
        return filename