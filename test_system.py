#!/usr/bin/env python3

import sys
import os
sys.path.append('Agentic-Automation')

from Source.Agents.WriterAgent import WriterAgent
from Source.Agents.CodingAgent import CodingAgent

def test_writer():
    print("🧪 Testing WriterAgent...")
    writer = WriterAgent()
    result = writer.write_report(
        topic="Binary Search Algorithm",
        requirements="Write a brief technical overview with complexity analysis"
    )
    print(f"✅ Writer test completed: {result}")

def test_coder():
    print("🧪 Testing CodingAgent...")
    coder = CodingAgent()
    result = coder.write_code(
        task="simple hello world",
        language="python"
    )
    print(f"✅ Coder test completed: {result['test_result']['status']}")

if __name__ == "__main__":
    print("🎓 Testing University Automation System Components\n")
    
    try:
        test_writer()
        print()
        test_coder()
        print("\n✅ All tests passed! System is ready.")
    except Exception as e:
        print(f"❌ Test failed: {e}")