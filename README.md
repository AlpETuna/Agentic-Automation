# University Automation System

An intelligent multi-agent system designed to automate computer science university tasks using the Strands library and swarm intelligence.

## Features

### 🤖 Specialized Agents

- **WriterAgent**: Creates academic reports, essays, and documentation with markdown and PDF output
- **CodingAgent**: Writes, tests, and executes code with automatic error detection
- **GitAgent**: Manages version control with intelligent commit messages and repository operations
- **RAGAgent**: Stores and retrieves course materials, rubrics, and notes using AWS Bedrock

### 🎯 Capabilities

- Write and format academic reports
- Code programming assignments with automatic testing
- Manage Git repositories and version control
- Store and query course materials using RAG
- Upload and index notes, rubrics, and assignments
- Handle complex multi-step academic workflows

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials:
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

3. Set up AWS S3 bucket for RAG storage (optional)

## Usage

### Interactive Mode
```bash
python main.py
```

### Example Commands

- "Write a report on machine learning algorithms"
- "Code a binary search tree implementation in Python"
- "Upload my course notes on data structures"
- "Commit my latest assignment to Git"
- "Find information about the grading rubric for project 2"

### Upload Documents
```bash
/upload path/to/document.pdf notes
/upload rubric.txt rubric
/upload lecture_slides.pdf course_material
```

## Architecture

The system uses a swarm-based approach where specialized agents collaborate:

1. **Orchestrator** analyzes requests and coordinates agents
2. **RAG system** provides contextual information from stored materials
3. **Specialized agents** handle specific tasks (writing, coding, Git)
4. **Swarm intelligence** manages complex multi-step workflows

## AWS Integration

- **Bedrock**: For embeddings and LLM capabilities
- **S3**: Document storage and retrieval
- **FAISS**: Local vector storage for fast similarity search