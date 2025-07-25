#!/usr/bin/env python3

import os
import sys
sys.path.append('Agentic-Automation')

from Source.Agents.RAGAgent import RAGAgent

def upload_document(file_path, doc_type="notes"):
    """Helper function to upload documents to the RAG system"""
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return False
    
    # Initialize RAG agent
    rag = RAGAgent()
    
    # Upload document
    result = rag.upload_document(file_path, doc_type)
    
    if result["status"] == "success":
        print(f"✅ Document uploaded successfully: {file_path}")
        print(f"📁 Type: {doc_type}")
        return True
    else:
        print(f"❌ Upload failed: {result['message']}")
        return False

def bulk_upload(directory, doc_type="notes"):
    """Upload all text files from a directory"""
    
    if not os.path.exists(directory):
        print(f"❌ Directory not found: {directory}")
        return
    
    uploaded = 0
    failed = 0
    
    for filename in os.listdir(directory):
        if filename.endswith(('.txt', '.md', '.py', '.js', '.java', '.cpp')):
            file_path = os.path.join(directory, filename)
            if upload_document(file_path, doc_type):
                uploaded += 1
            else:
                failed += 1
    
    print(f"\n📊 Upload Summary:")
    print(f"✅ Uploaded: {uploaded}")
    print(f"❌ Failed: {failed}")

if __name__ == "__main__":
    print("📚 Document Upload Helper")
    print("Usage examples:")
    print("  python upload_helper.py")
    print("  Then follow the prompts")
    
    while True:
        print("\nOptions:")
        print("1. Upload single file")
        print("2. Bulk upload from directory") 
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            file_path = input("Enter file path: ").strip()
            doc_type = input("Enter document type (notes/rubric/course_material/assignment): ").strip() or "notes"
            upload_document(file_path, doc_type)
            
        elif choice == "2":
            directory = input("Enter directory path: ").strip()
            doc_type = input("Enter document type (notes/rubric/course_material/assignment): ").strip() or "notes"
            bulk_upload(directory, doc_type)
            
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")