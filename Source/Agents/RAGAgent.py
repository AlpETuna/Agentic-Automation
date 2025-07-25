from strands import Agent
import boto3
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
# from PyPDF2 import PdfReader  # Optional - fallback to text files only
import json
from datetime import datetime

class RAGAgent:
    def __init__(self, aws_region="us-east-1"):
        self.agent = Agent(
            name="rag_specialist",
            system_prompt="""You are a RAG (Retrieval Augmented Generation) specialist.
            You help store, retrieve, and synthesize information from course materials,
            rubrics, and notes to provide contextual answers for university tasks."""
        )
        
        # AWS setup
        self.bedrock = boto3.client('bedrock-runtime', region_name=aws_region)
        self.s3 = boto3.client('s3', region_name=aws_region)
        self.bucket_name = "university-rag-storage"  # Configure this
        
        # Vector store setup
        self.embeddings = BedrockEmbeddings(
            client=self.bedrock,
            model_id="amazon.titan-embed-text-v1"
        )
        
        self.vector_store = None
        self._load_vector_store()
    
    def upload_document(self, file_path, document_type="notes"):
        """Upload document to S3 and add to vector store"""
        try:
            # Upload to S3
            s3_key = f"{document_type}/{os.path.basename(file_path)}"
            self.s3.upload_file(file_path, self.bucket_name, s3_key)
            
            # Process for vector store
            self._process_document(file_path, document_type)
            
            return {
                "status": "success",
                "s3_location": f"s3://{self.bucket_name}/{s3_key}",
                "message": "Document uploaded and indexed"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query_knowledge_base(self, query, document_type=None, k=5):
        """Query the knowledge base for relevant information"""
        try:
            if not self.vector_store:
                return {"status": "error", "message": "No knowledge base loaded"}
            
            # Retrieve relevant documents
            docs = self.vector_store.similarity_search(query, k=k)
            
            # Filter by document type if specified
            if document_type:
                docs = [doc for doc in docs if doc.metadata.get('type') == document_type]
            
            # Generate response using retrieved context
            context = "\n\n".join([doc.page_content for doc in docs])
            
            prompt = f"""
            Based on the following context from course materials:
            
            {context}
            
            Answer this question: {query}
            
            Provide a comprehensive answer citing the relevant sources.
            """
            
            response = self.agent(prompt)
            
            return {
                "status": "success",
                "answer": str(response),
                "sources": [doc.metadata for doc in docs]
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def _process_document(self, file_path, document_type):
        """Process document and add to vector store"""
        # Load document
        if file_path.endswith('.pdf'):
            return {"status": "error", "message": "PDF support requires PyPDF2. Please convert to text file."}
        else:
            loader = TextLoader(file_path)
            documents = loader.load()
        
        # Split text
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Add metadata
        for split in splits:
            split.metadata.update({
                'type': document_type,
                'source': file_path,
                'timestamp': datetime.now().isoformat()
            })
        
        # Add to vector store
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(splits, self.embeddings)
        else:
            self.vector_store.add_documents(splits)
        
        # Save vector store
        self._save_vector_store()
    
    def _load_vector_store(self):
        """Load existing vector store"""
        try:
            if os.path.exists("vector_store"):
                self.vector_store = FAISS.load_local("vector_store", self.embeddings)
        except:
            pass
    
    def _extract_pdf_text(self, file_path):
        """Extract text from PDF file"""
        with open(file_path, 'rb') as file:
            reader = PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()
        return text
    
    def _save_vector_store(self):
        """Save vector store locally"""
        if self.vector_store:
            self.vector_store.save_local("vector_store")