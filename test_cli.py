#!/usr/bin/env python3
"""
Test script for Perplexity CLI API integration.
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import PerplexityAPI


def test_streaming_chat():
    """Test streaming chat functionality."""
    print("=" * 50)
    print("Test 1: Streaming Chat")
    print("=" * 50)
    
    api = PerplexityAPI()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
        {"role": "user", "content": "What is 2 + 2? Answer in one sentence."}
    ]
    
    print("Question: What is 2 + 2?")
    print("Response: ", end="", flush=True)
    
    full_response = ""
    for chunk in api.chat(messages, model="sonar", stream=True):
        print(chunk, end="", flush=True)
        full_response += chunk
    
    print("\n")
    
    if full_response:
        print("✅ Streaming chat test PASSED")
        return True
    else:
        print("❌ Streaming chat test FAILED")
        return False


def test_sync_chat():
    """Test non-streaming chat functionality."""
    print("=" * 50)
    print("Test 2: Synchronous Chat")
    print("=" * 50)
    
    api = PerplexityAPI()
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Keep responses brief."},
        {"role": "user", "content": "Name one planet in our solar system."}
    ]
    
    print("Question: Name one planet in our solar system.")
    
    # Use sync mode
    result = api._sync_response(
        {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {api.api_key}",
        },
        {"model": "sonar", "messages": messages, "stream": False}
    )
    
    print(f"Response: {result.get('content', 'No response')}")
    print()
    
    if result.get("content"):
        print("✅ Sync chat test PASSED")
        return True
    else:
        print("❌ Sync chat test FAILED")
        return False


def test_session():
    """Test session save/load functionality."""
    print("=" * 50)
    print("Test 3: Session Management")
    print("=" * 50)
    
    from session import Session
    import tempfile
    import shutil
    
    # Use temp directory for test
    temp_dir = tempfile.mkdtemp()
    
    try:
        session = Session(session_dir=temp_dir)
        
        # Add messages
        session.add_message("user", "Hello!")
        session.add_message("assistant", "Hi there!")
        session.add_message("user", "How are you?")
        
        # Save session
        filename = session.save("test_session")
        print(f"Saved session: {filename}")
        
        # Create new session and load
        session2 = Session(session_dir=temp_dir)
        loaded = session2.load("test_session")
        
        if loaded and len(session2.messages) == 3:
            print(f"Loaded session with {len(session2.messages)} messages")
            print("✅ Session management test PASSED")
            return True
        else:
            print("❌ Session management test FAILED")
            return False
    finally:
        shutil.rmtree(temp_dir)


def test_config():
    """Test configuration management."""
    print("=" * 50)
    print("Test 4: Configuration")
    print("=" * 50)
    
    from config import Config
    import tempfile
    
    temp_file = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
    temp_file.close()
    
    try:
        config = Config(config_path=temp_file.name)
        
        # Test defaults
        print(f"Default model: {config.model}")
        print(f"Default input limit: {config.input_token_limit}")
        
        # Test setting values
        config.model = "sonar-reasoning"
        config.system_prompt = "Test prompt"
        config.save()
        
        # Reload and verify
        config2 = Config(config_path=temp_file.name)
        
        if config2.model == "sonar-reasoning" and config2.system_prompt == "Test prompt":
            print("✅ Configuration test PASSED")
            return True
        else:
            print("❌ Configuration test FAILED")
            return False
    finally:
        os.unlink(temp_file.name)


def main():
    """Run all tests."""
    print("\n🧪 Perplexity CLI Integration Tests\n")
    
    results = []
    
    results.append(("Streaming Chat", test_streaming_chat()))
    results.append(("Sync Chat", test_sync_chat()))
    results.append(("Session Management", test_session()))
    results.append(("Configuration", test_config()))
    
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
