"""
Direct Groq API client for Kimi K2 model.
Bypasses claude-code-router for fast, reliable inference.

Usage:
    # As a module
    from groq_kimi import query_kimi, generate_report

    response = query_kimi("What is 2+2?")
    report = generate_report("Analyze Q4 2024 sales data")

    # From command line
    python groq_kimi.py "Your prompt here"
    python groq_kimi.py --report "Generate a summary of..."
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Fix Windows encoding issues
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set. Add it to .env file.")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_MODEL = "moonshotai/kimi-k2-instruct-0905"


def query_kimi(
    prompt: str,
    *,
    system_prompt: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 16384,
    temperature: float = 0.7,
    stream: bool = False,
) -> str:
    """
    Query Groq's Kimi K2 model directly.

    Args:
        prompt: The user message/question
        system_prompt: Optional system instructions
        model: Model ID (default: moonshotai/kimi-k2-instruct-0905)
        max_tokens: Maximum response tokens (default: 16384)
        temperature: Creativity (0.0-2.0, default: 0.7)
        stream: Whether to stream the response (default: False)

    Returns:
        The model's response text
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": stream,
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(timeout=120.0) as client:
        response = client.post(GROQ_API_URL, json=payload, headers=headers)
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]


def generate_report(
    topic: str,
    *,
    context: str | None = None,
    format_type: str = "markdown",
    max_tokens: int = 16384,
) -> str:
    """
    Generate a structured report on a given topic.

    Args:
        topic: The subject of the report
        context: Additional context or data to include
        format_type: Output format (markdown, plain, json)
        max_tokens: Maximum response tokens

    Returns:
        Generated report content
    """
    system_prompt = f"""You are an expert analyst. Generate comprehensive, well-structured reports.
Output format: {format_type}
Be concise but thorough. Use data and specific examples where possible."""

    prompt = f"Generate a detailed report on: {topic}"

    if context:
        prompt += f"\n\nAdditional context:\n{context}"

    return query_kimi(
        prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=0.5,  # Lower temperature for more focused reports
    )


def chat_session():
    """Interactive chat session with Kimi K2."""
    print("Kimi K2 Chat (type 'quit' to exit)")
    print("-" * 40)

    messages = []

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        messages.append({"role": "user", "content": user_input})

        payload = {
            "model": DEFAULT_MODEL,
            "messages": messages,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(GROQ_API_URL, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()
                assistant_msg = data["choices"][0]["message"]["content"]

                messages.append({"role": "assistant", "content": assistant_msg})
                print(f"\nKimi: {assistant_msg}")

        except httpx.HTTPStatusError as e:
            print(f"\nError: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"\nError: {e}")


def main():
    parser = argparse.ArgumentParser(description="Query Groq's Kimi K2 model")
    parser.add_argument("prompt", nargs="?", help="The prompt to send")
    parser.add_argument("--report", "-r", action="store_true", help="Generate a report")
    parser.add_argument("--chat", "-c", action="store_true", help="Start interactive chat")
    parser.add_argument("--context", help="Additional context for reports")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Model to use")
    parser.add_argument("--max-tokens", type=int, default=16384, help="Max tokens")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    parser.add_argument("--output", "-o", help="Output file path (saves response to file)")

    args = parser.parse_args()

    if args.chat:
        chat_session()
        return

    if not args.prompt:
        parser.print_help()
        return

    try:
        if args.report:
            result = generate_report(
                args.prompt,
                context=args.context,
                max_tokens=args.max_tokens,
            )
        else:
            result = query_kimi(
                args.prompt,
                model=args.model,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
            )

        if args.output:
            Path(args.output).write_text(result, encoding="utf-8")
            print(f"Output saved to: {args.output}")
        else:
            print(result)

    except httpx.HTTPStatusError as e:
        print(f"API Error: {e.response.status_code}", file=sys.stderr)
        print(e.response.text, file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
