import argparse
import sys
from langchain_ollama import OllamaLLM


def main():
    # Set up command-line argument parser
    parser = argparse.ArgumentParser(
        description="Generate text using Ollama models via LangChain."
    )

    # Positional argument for the prompt
    parser.add_argument(
        "prompt",
        nargs="?",
        type=str,
        help="The input prompt/question for the model.",
    )

    # Optional argument for selecting the model
    parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="qwen3:0.6b",
        help="Ollama model name (default: qwen3:0.6b)",
    )

    args = parser.parse_args()

    # Read prompt from positional argument or pipe input
    if args.prompt:
        user_prompt = args.prompt
    elif not sys.stdin.isatty():
        user_prompt = sys.stdin.read().strip()
    else:
        parser.print_help()
        sys.exit(1)

    # Initialize and run the LLM
    llm = OllamaLLM(model=args.model)
    response = llm.invoke(user_prompt)

    print(response)


if __name__ == "__main__":
    main()
    # python cli_chat.py "write a program to read excel file using python pandas"