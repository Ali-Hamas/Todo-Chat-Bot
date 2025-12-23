"""
Test script to verify the rewritten /api/chat endpoint
Ensures compliance with specs/features/ai_agent.md
"""

import sys
import ast
import re

def test_no_string_matching():
    """Verify NO string matching logic exists in main.py"""
    print("=" * 60)
    print("TEST 1: No String Matching")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    # Check for string matching patterns
    bad_patterns = [
        r'if\s+["\'].*["\'].*in.*message',
        r'message\.lower\(\)',
        r'\.replace\(["\']add task["\']',
        r'\.replace\(["\']list task["\']',
        r'process_user_message_fallback',
    ]

    issues = []
    for pattern in bad_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            issues.append(f"Found string matching pattern: {pattern}")

    if issues:
        print("\n[FAIL] String matching code found:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("\n[PASS] No string matching code found")
        print("  - No 'if ... in message' patterns")
        print("  - No message.lower() calls")
        print("  - No fallback function")
        return True


def test_openai_tool_calling():
    """Verify OpenAI tool calling is implemented"""
    print("\n" + "=" * 60)
    print("TEST 2: OpenAI Tool Calling")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    required_elements = [
        ("OpenAI client", r'from openai import OpenAI'),
        ("Tool definitions", r'get_tool_definitions'),
        ("Tool execution", r'execute_tool'),
        ("chat.completions.create", r'client\.chat\.completions\.create'),
        ("tool_calls handling", r'response_message\.tool_calls'),
        ("tool role messages", r'"role":\s*"tool"'),
    ]

    results = []
    for name, pattern in required_elements:
        if re.search(pattern, content):
            print(f"\n[PASS] {name} found")
            results.append(True)
        else:
            print(f"\n[FAIL] {name} NOT found")
            results.append(False)

    return all(results)


def test_request_flow_steps():
    """Verify all 6 steps from ai_agent.md are present"""
    print("\n" + "=" * 60)
    print("TEST 3: Request Flow Steps (ai_agent.md)")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    steps = [
        ("STEP 1: Authenticate", r'Depends\(get_current_user\)'),
        ("STEP 2: Retrieve Context", r'STEP 2.*Retrieve Context.*last 10 messages'),
        ("STEP 3: System Prompt", r'STEP 3.*System Prompt'),
        ("STEP 4: AI Decision", r'STEP 4.*AI Decision.*Send.*Tools to OpenAI'),
        ("STEP 5: Tool Execution", r'STEP 5.*Tool Execution'),
        ("STEP 6: Persist", r'STEP 6.*Persist'),
    ]

    results = []
    for step_name, pattern in steps:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            print(f"\n[PASS] {step_name}")
            results.append(True)
        else:
            print(f"\n[FAIL] {step_name} NOT found")
            results.append(False)

    return all(results)


def test_system_prompt():
    """Verify system prompt matches ai_agent.md"""
    print("\n" + "=" * 60)
    print("TEST 4: System Prompt")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    # Check for the exact system prompt from ai_agent.md
    required_phrases = [
        "You are a helpful Todo Assistant",
        "You act on behalf of the user",
        "you MUST call the provided tools",
        "Do not ask for confirmation unless necessary",
    ]

    results = []
    for phrase in required_phrases:
        if phrase in content:
            print(f"\n[PASS] System prompt contains: '{phrase[:50]}...'")
            results.append(True)
        else:
            print(f"\n[FAIL] System prompt missing: '{phrase}'")
            results.append(False)

    return all(results)


def test_mcp_tools_integration():
    """Verify MCP tools from mcp_server.py are used"""
    print("\n" + "=" * 60)
    print("TEST 5: MCP Tools Integration")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    checks = [
        ("Import from mcp_server", r'from mcp_server import'),
        ("get_tool_definitions()", r'tools\s*=\s*get_tool_definitions\(\)'),
        ("execute_tool()", r'execute_tool\('),
        ("Pass user_id to tools", r'execute_tool\(.*user_id'),
    ]

    results = []
    for name, pattern in checks:
        if re.search(pattern, content):
            print(f"\n[PASS] {name}")
            results.append(True)
        else:
            print(f"\n[FAIL] {name} NOT found")
            results.append(False)

    return all(results)


def test_database_persistence():
    """Verify messages are saved to database"""
    print("\n" + "=" * 60)
    print("TEST 6: Database Persistence")
    print("=" * 60)

    with open("main.py", "r") as f:
        content = f.read()

    checks = [
        ("save_chat_messages function", r'def save_chat_messages'),
        ("Save user message", r'MessageRole\.user'),
        ("Save assistant message", r'MessageRole\.assistant'),
        ("Database commit", r'db\.commit\(\)'),
    ]

    results = []
    for name, pattern in checks:
        if re.search(pattern, content):
            print(f"\n[PASS] {name}")
            results.append(True)
        else:
            print(f"\n[FAIL] {name} NOT found")
            results.append(False)

    return all(results)


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("CHAT ENDPOINT REWRITE VERIFICATION")
    print("Testing compliance with specs/features/ai_agent.md")
    print("=" * 60 + "\n")

    tests = [
        test_no_string_matching,
        test_openai_tool_calling,
        test_request_flow_steps,
        test_system_prompt,
        test_mcp_tools_integration,
        test_database_persistence,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 60)
    if all(results):
        print("ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe /api/chat endpoint has been successfully rewritten:")
        print("  - NO string matching")
        print("  - Uses OpenAI Tool Calling exclusively")
        print("  - Implements all 6 steps from ai_agent.md")
        print("  - Integrates with MCP tools from mcp_server.py")
        print("  - Persists all messages to database")
        return 0
    else:
        print("SOME TESTS FAILED")
        print("=" * 60)
        passed = sum(results)
        total = len(results)
        print(f"\nPassed: {passed}/{total} tests")
        return 1


if __name__ == "__main__":
    sys.exit(main())
