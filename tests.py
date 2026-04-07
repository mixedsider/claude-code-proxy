#!/usr/bin/env python3
"""
Comprehensive test suite for Claude-on-OpenAI Proxy.

This script provides tests for:
1. Integration tests: Streaming and non-streaming requests with various scenarios.
2. Unit tests: Verification of Anthropic-to-OpenAI format conversion.

Usage:
  python tests.py                    # Run all tests
  python tests.py --no-streaming     # Skip streaming (integration) tests
  python tests.py --simple           # Run only simple integration tests
  python tests.py --tools            # Run tool-related integration tests only
  python tests.py --proxy-only       # Only test the proxy (ignore Anthropic comparison)
  python tests.py --unit-only        # Run only internal format conversion unit tests
"""

import os
import json
import time
import httpx
import argparse
import asyncio
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional, Set
from dotenv import load_dotenv

# Import server components for unit testing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from server import (
    MessagesRequest,
    ContentBlockText,
    ContentBlockToolUse,
    ContentBlockToolResult,
    Message,
    convert_anthropic_to_litellm,
)

# Load environment variables
load_dotenv()

# Configuration
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
PROXY_API_KEY = os.environ.get("ANTHROPIC_API_KEY")  # Using same key for proxy
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
PROXY_API_URL = "http://localhost:8082/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
MODEL = "claude-3-sonnet-20240229"  # Change to your preferred model

# Headers
anthropic_headers = {
    "x-api-key": ANTHROPIC_API_KEY,
    "anthropic-version": ANTHROPIC_VERSION,
    "content-type": "application/json",
}

proxy_headers = {
    "x-api-key": PROXY_API_KEY,
    "anthropic-version": ANTHROPIC_VERSION,
    "content-type": "application/json",
}

# Tool definitions
calculator_tool = {
    "name": "calculator",
    "description": "Evaluate mathematical expressions",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "The mathematical expression to evaluate"
            }
        },
        "required": ["expression"]
    }
}

weather_tool = {
    "name": "weather",
    "description": "Get weather information for a location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city or location to get weather for"
            },
            "units": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature units"
            }
        },
        "required": ["location"]
    }
}

search_tool = {
    "name": "search",
    "description": "Search for information on the web",
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string", 
                "description": "The search query"
            }
        },
        "required": ["query"]
    }
}

# Test scenarios
TEST_SCENARIOS = {
    # Simple text response
    "simple": {
        "model": MODEL,
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": "Hello, world! Can you tell me about Paris in 2-3 sentences?"}
        ]
    },
    
    # Basic tool use
    "calculator": {
        "model": MODEL,
        "max_tokens": 300,
        "messages": [
            {"role": "user", "content": "What is 135 + 7.5 divided by 2.5?"}
        ],
        "tools": [calculator_tool],
        "tool_choice": {"type": "auto"}
    },
    
    # Multiple tools
    "multi_tool": {
        "model": MODEL,
        "max_tokens": 500,
        "temperature": 0.7,
        "top_p": 0.95,
        "system": "You are a helpful assistant that uses tools when appropriate. Be concise and precise.",
        "messages": [
            {"role": "user", "content": "I'm planning a trip to New York next week. What's the weather like and what are some interesting places to visit?"}
        ],
        "tools": [weather_tool, search_tool],
        "tool_choice": {"type": "auto"}
    },
    
    # Multi-turn conversation
    "multi_turn": {
        "model": MODEL,
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": "Let's do some math. What is 240 divided by 8?"},
            {"role": "assistant", "content": "To calculate 240 divided by 8, I'll perform the division:\n\n240 \u00f7 8 = 30\n\nSo the result is 30."},
            {"role": "user", "content": "Now multiply that by 4 and tell me the result."}
        ],
        "tools": [calculator_tool],
        "tool_choice": {"type": "auto"}
    },
    
    # Content blocks
    "content_blocks": {
        "model": MODEL,
        "max_tokens": 500,
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": "I need to know the weather in Los Angeles and calculate 75.5 / 5. Can you help with both?"}
            ]}
        ],
        "tools": [calculator_tool, weather_tool],
        "tool_choice": {"type": "auto"}
    },
    
    # Simple streaming test
    "simple_stream": {
        "model": MODEL,
        "max_tokens": 100,
        "stream": True,
        "messages": [
            {"role": "user", "content": "Count from 1 to 5, with one number per line."}
        ]
    },
    
    # Tool use with streaming
    "calculator_stream": {
        "model": MODEL,
        "max_tokens": 300,
        "stream": True,
        "messages": [
            {"role": "user", "content": "What is 135 + 17.5 divided by 2.5?"}
        ],
        "tools": [calculator_tool],
        "tool_choice": {"type": "auto"}
    },

    # Ollama test (local)
    "ollama": {
        "model": "ollama/qwen3.5:0.8b", # Updated to use your local model
        "max_tokens": 100,
        "messages": [
            {"role": "user", "content": "Hi! Just say 'Ollama is working' if you can hear me."}
        ]
    },

    # --- 3-Tier Mapping Tests (Integrated from test_all.py) ---
    "tier_big": {
        "model": "claude-3-opus-20240229",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "hi"}]
    },
    "tier_middle": {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "hi"}]
    },
    "tier_small": {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 100,
        "messages": [{"role": "user", "content": "hi"}]
    },
    "tier_small_tool": {
        "model": "claude-3-haiku-20240307",
        "max_tokens": 1024,
        "messages": [
            {"role": "user", "content": "What is 123 + 456? Use the calculator tool."}
        ],
        "tools": [
            {
                "name": "calculator",
                "description": "A simple calculator for addition",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["a", "b"]
                }
            }
        ],
        "tool_choice": {"type": "auto"}
    }
}

# Required event types for Anthropic streaming responses
REQUIRED_EVENT_TYPES = {
    "message_start", 
    "content_block_start", 
    "content_block_delta", 
    "content_block_stop", 
    "message_delta", 
    "message_stop"
}

# ================= UNIT TESTS (Internal Format Conversion) =================

def make_unit_msg_request(messages, tools=None):
    """Internal helper to create MessagesRequest for unit tests."""
    return MessagesRequest(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=messages,
        tools=tools,
    )

def test_unit_tool_use_to_openai():
    """Unit test: assistant tool_use block to OpenAI tool_calls conversion."""
    print("Running case: test_unit_tool_use_to_openai...")
    messages = [
        Message(role="user", content="Show files"),
        Message(
            role="assistant",
            content=[
                ContentBlockToolUse(
                    type="tool_use",
                    id="toolu_01abc",
                    name="Bash",
                    input={"command": "ls -la"},
                )
            ],
        ),
    ]
    result = convert_anthropic_to_litellm(make_unit_msg_request(messages))
    msgs = result["messages"]

    assistant_msg = next((m for m in msgs if m["role"] == "assistant"), None)
    if not assistant_msg: return False, "Assistant message not found"
    if "tool_calls" not in assistant_msg: return False, "tool_calls missing in assistant message"
    
    tc = assistant_msg["tool_calls"][0]
    if tc["id"] != "toolu_01abc": return False, f"ID mismatch: {tc['id']}"
    if tc["function"]["name"] != "Bash": return False, "Name mismatch"
    
    args = json.loads(tc["function"]["arguments"])
    if args["command"] != "ls -la": return False, "Arguments mismatch"
    
    return True, "PASSED"

def test_unit_tool_result_to_role_tool():
    """Unit test: user tool_result block to role='tool' conversion."""
    print("Running case: test_unit_tool_result_to_role_tool...")
    messages = [
        Message(role="user", content="Show files"),
        Message(
            role="assistant",
            content=[
                ContentBlockToolUse(type="tool_use", id="toolu_01abc", name="Bash", input={"command": "ls"})
            ],
        ),
        Message(
            role="user",
            content=[
                ContentBlockToolResult(
                    type="tool_result",
                    tool_use_id="toolu_01abc",
                    content="file1.txt",
                )
            ],
        ),
    ]
    result = convert_anthropic_to_litellm(make_unit_msg_request(messages))
    msgs = result["messages"]

    tool_msg = next((m for m in msgs if m.get("role") == "tool"), None)
    if not tool_msg: return False, "Role 'tool' message not found"
    if tool_msg["tool_call_id"] != "toolu_01abc": return False, "tool_call_id mismatch"
    if tool_msg["content"] != "file1.txt": return False, "Content mismatch"
    
    return True, "PASSED"

def test_unit_no_plain_text_tool_pattern():
    """Unit test: Verify that the textual [Tool: ...] pattern is NOT generated."""
    print("Running case: test_unit_no_plain_text_tool_pattern...")
    messages = [
        Message(role="user", content="Do something"),
        Message(
            role="assistant",
            content=[
                ContentBlockText(type="text", text="Executing..."),
                ContentBlockToolUse(type="tool_use", id="toolu_xyz", name="Bash", input={"command": "echo"}),
            ],
        ),
    ]
    result = convert_anthropic_to_litellm(make_unit_msg_request(messages))
    msgs = result["messages"]

    assistant_msg = next((m for m in msgs if m["role"] == "assistant"), None)
    content_str = str(assistant_msg.get("content", ""))
    
    if "[Tool:" in content_str: return False, f"Old text pattern found in content: {content_str}"
    if "tool_calls" not in assistant_msg: return False, "tool_calls missing"
    
    return True, "PASSED"

def run_unit_tests():
    """Run all internal unit tests."""
    print("\n\n=========== RUNNING INTERNAL UNIT TESTS ===========\n")
    unit_results = {}
    
    funcs = [
        ("test_unit_tool_use_to_openai", test_unit_tool_use_to_openai),
        ("test_unit_tool_result_to_role_tool", test_unit_tool_result_to_role_tool),
        ("test_unit_no_plain_text_tool_pattern", test_unit_no_plain_text_tool_pattern)
    ]
    
    for name, func in funcs:
        try:
            success, msg = func()
            unit_results[name] = success
            if success:
                print(f"✅ {name}: {msg}")
            else:
                print(f"❌ {name}: {msg}")
        except Exception as e:
            unit_results[name] = False
            print(f"❌ {name}: Error: {str(e)}")
            
    return unit_results

# ================= NON-STREAMING INTEGRATION TESTS =================

def get_response(url, headers, data):
    """Send a request and get the response."""
    start_time = time.time()
    response = httpx.post(url, headers=headers, json=data, timeout=60)
    elapsed = time.time() - start_time
    
    print(f"Response time: {elapsed:.2f} seconds")
    return response

def verify_proxy_response(proxy_response, check_tools=False):
    """Verify the proxy response structure without comparing to Anthropic."""
    try:
        proxy_json = proxy_response.json()
    except Exception as e:
        print(f"\u274c Failed to parse proxy response as JSON: {e}")
        print(f"Raw response: {proxy_response.text}")
        return False
    
    print("\n--- Proxy Response Structure ---")
    print(json.dumps({k: v for k, v in proxy_json.items() if k != "content"}, indent=2))
    print(f"Mapped Model: {proxy_json.get('model')}")
    
    # Basic structure verification
    assert proxy_json.get("role") == "assistant", "Proxy role is not 'assistant'"
    assert proxy_json.get("type") == "message", "Proxy type is not 'message'"
    
    valid_stop_reasons = ["end_turn", "max_tokens", "stop_sequence", "tool_use", None]
    assert proxy_json.get("stop_reason") in valid_stop_reasons, "Invalid stop reason"
    assert "content" in proxy_json, "No content in Proxy response"
    
    proxy_content = proxy_json["content"]
    assert isinstance(proxy_content, list), "Proxy content is not a list"
    assert len(proxy_content) > 0, "Proxy content is empty"
    
    # Print text preview if available
    proxy_text = next((item.get("text") for item in proxy_content if item.get("type") == "text"), None)
    if proxy_text:
        print("\n---------- PROXY TEXT PREVIEW ----------")
        print("\n".join(proxy_text.strip().split("\n")[:5]))
    
    if check_tools:
        proxy_tool = next((item for item in proxy_content if item.get("type") == "tool_use"), None)
        if proxy_tool:
            print("\n---------- PROXY TOOL USE ----------")
            print(json.dumps(proxy_tool, indent=2))
            assert proxy_tool.get("name"), "Tool use missing name"
            assert proxy_tool.get("input"), "Tool use missing input"
        else:
            print("\n\u26a0\ufe0f Proxy response does not contain tool use")
            
    return True

def compare_responses(anthropic_response, proxy_response, check_tools=False):
    """Compare the two responses to see if they're similar enough."""
    anthropic_json = anthropic_response.json()
    proxy_json = proxy_response.json()
    
    print("\n--- Anthropic Response Structure ---")
    print(json.dumps({k: v for k, v in anthropic_json.items() if k != "content"}, indent=2))
    
    print("\n--- Proxy Response Structure ---")
    print(json.dumps({k: v for k, v in proxy_json.items() if k != "content"}, indent=2))
    
    # Basic structure verification
    assert proxy_json.get("role") == "assistant", "Proxy role is not 'assistant'"
    assert proxy_json.get("type") == "message", "Proxy type is not 'message'"
    
    valid_stop_reasons = ["end_turn", "max_tokens", "stop_sequence", "tool_use", None]
    assert proxy_json.get("stop_reason") in valid_stop_reasons, "Invalid stop reason"
    
    assert "content" in anthropic_json, "No content in Anthropic response"
    assert "content" in proxy_json, "No content in Proxy response"
    
    # Check if content has text
    anthropic_text = next((item.get("text") for item in anthropic_json["content"] if item.get("type") == "text"), None)
    proxy_text = next((item.get("text") for item in proxy_json["content"] if item.get("type") == "text"), None)
    
    if anthropic_text:
        print(f"\n---------- ANTHROPIC TEXT PREVIEW ----------\n{anthropic_text[:200]}...")
    if proxy_text:
        print(f"\n---------- PROXY TEXT PREVIEW ----------\n{proxy_text[:200]}...")
    
    return True

def test_request(test_name, request_data, check_tools=False, proxy_only=False):
    """Run an integration test with the given request data."""
    print(f"\n{'='*20} RUNNING INTEGRATION TEST: {test_name} {'='*20}")
    
    anthropic_data = request_data.copy()
    proxy_data = request_data.copy()
    
    try:
        print("\nSending to Proxy...")
        proxy_response = get_response(PROXY_API_URL, proxy_headers, proxy_data)
        
        if proxy_response.status_code != 200:
            print(f"❌ Proxy failed status {proxy_response.status_code}: {proxy_response.text}")
            return False

        if proxy_only:
            return verify_proxy_response(proxy_response, check_tools=check_tools)

        print("\nSending to Anthropic API...")
        anthropic_response = get_response(ANTHROPIC_API_URL, anthropic_headers, anthropic_data)
        
        if anthropic_response.status_code != 200:
            print(f"⚠️ Anthropic failed: {anthropic_response.text}")
            return verify_proxy_response(proxy_response, check_tools=check_tools)
        
        return compare_responses(anthropic_response, proxy_response, check_tools=check_tools)
    
    except Exception as e:
        print(f"❌ Error in test {test_name}: {str(e)}")
        return False

# ================= STREAMING INTEGRATION TESTS =================

class StreamStats:
    def __init__(self):
        self.event_types = set()
        self.event_counts = {}
        self.total_chunks = 0
        self.text_content = ""
        self.has_tool_use = False
        self.has_error = False
        self.error_message = ""
        
    def add_event(self, event_data):
        self.total_chunks += 1
        event_type = event_data.get("type")
        if event_type:
            self.event_types.add(event_type)
            self.event_counts[event_type] = self.event_counts.get(event_type, 0) + 1
            if event_type == "content_block_start" and event_data.get("content_block", {}).get("type") == "tool_use":
                self.has_tool_use = True
            elif event_type == "content_block_delta" and "delta" in event_data:
                self.text_content += event_data["delta"].get("text", "")
                
    def summarize(self):
        print(f"Chunks: {self.total_chunks}, ToolUse: {self.has_tool_use}")
        if self.text_content:
            print(f"Text: {self.text_content[:100]}...")

async def stream_response(url, headers, data, stream_name):
    print(f"\nStarting {stream_name} stream...")
    stats = StreamStats()
    try:
        async with httpx.AsyncClient() as client:
            request_data = data.copy()
            request_data["stream"] = True
            async with client.stream("POST", url, json=request_data, headers=headers, timeout=30) as response:
                if response.status_code != 200:
                    stats.has_error = True
                    stats.error_message = f"HTTP {response.status_code}"
                    return stats, stats.error_message
                
                async for chunk in response.aiter_text():
                    for line in chunk.split("\n"):
                        if line.startswith("data: "):
                            data_part = line[6:].strip()
                            if data_part == "[DONE]": continue
                            try: stats.add_event(json.loads(data_part))
                            except: pass
    except Exception as e:
        stats.has_error = True
        return stats, str(e)
    return stats, None

async def test_streaming(test_name, request_data, proxy_only=False):
    print(f"\n{'='*20} RUNNING STREAMING TEST: {test_name} {'='*20}")
    proxy_stats, proxy_err = await stream_response(PROXY_API_URL, proxy_headers, request_data, "Proxy")
    proxy_stats.summarize()
    if proxy_err: return False
    return not proxy_stats.has_error and (len(proxy_stats.text_content) > 0 or proxy_stats.has_tool_use)

# ================= MAIN =================

async def run_tests(args):
    results = {}
    
    # 1. Internal Unit Tests
    if not args.streaming_only and not args.integration_only:
        unit_res = run_unit_tests()
        results.update(unit_res)
        if args.unit_only:
            return all(unit_res.values())

    # 2. Integration Tests (Non-streaming)
    if not args.streaming_only and not args.unit_only:
        print("\n\n=========== RUNNING NON-STREAMING INTEGRATION TESTS ===========\n")
        for name, data in TEST_SCENARIOS.items():
            if args.test and args.test != name: continue
            if data.get("stream"): continue
            if args.simple and "tools" in data: continue
            if args.tools_only and "tools" not in data: continue
            
            results[name] = test_request(name, data, check_tools="tools" in data, proxy_only=args.proxy_only)

    # 3. Integration Tests (Streaming)
    if not args.no_streaming and not args.unit_only:
        print("\n\n=========== RUNNING STREAMING INTEGRATION TESTS ===========\n")
        for name, data in TEST_SCENARIOS.items():
            if args.test and args.test != name: continue
            if not data.get("stream") and not name.endswith("_stream"): continue
            
            results[f"{name}_stream"] = await test_streaming(name, data, proxy_only=args.proxy_only)

    # Summary
    print("\n\n=========== TEST SUMMARY ===========\n")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    for t, res in results.items():
        print(f"{t}: {'PASS' if res else 'FAIL'}")
    print(f"\nTotal: {passed}/{total} tests passed")
    return passed == total

async def main():
    parser = argparse.ArgumentParser(description="Test suite for Claude Proxy")
    parser.add_argument("--no-streaming", action="store_true", help="Skip streaming tests")
    parser.add_argument("--streaming-only", action="store_true", help="Only run streaming tests")
    parser.add_argument("--simple", action="store_true", help="No tool tests")
    parser.add_argument("--tools-only", action="store_true", help="Only tool tests")
    parser.add_argument("--proxy-only", action="store_true", help="Skip Anthropic comparison")
    parser.add_argument("--unit-only", action="store_true", help="Only run unit tests")
    parser.add_argument("--integration-only", action="store_true", help="Only run integration tests")
    parser.add_argument("--test", type=str, help="Specific test case")
    parser.add_argument("--tiers", action="store_true", help="Run tier mapping tests")
    args = parser.parse_args()
    
    if not ANTHROPIC_API_KEY and not args.proxy_only:
        print("Warning: ANTHROPIC_API_KEY not set. Using --proxy-only mode automatically.")
        args.proxy_only = True
        
    success = await run_tests(args)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())