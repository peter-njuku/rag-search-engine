#!/usr/bin/env python3

import argparse

from cli.lib.semantic_search import embed_text, verify_model

def main():
    parser = argparse.ArgumentParser(description="Semantic Search CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    verify_parser = subparsers.add_parser("verify", help="Verify that the semantic search model loads correctly")
    
    embed_parser = subparsers.add_parser("embed_text", help="Generate an embedding for a given text")
    embed_parser.add_argument("text", type=str, help="The text to generate an embedding for")

    args = parser.parse_args()

    match args.command:
        case "verify":
            verify_model()

        case "embed_text":
            if not args.text:
                parser.error("the 'text' argument is required for the 'embed_text' command")
            embed_text(args.text)

        case _:
            parser.print_help()

if __name__ == "__main__":
    main()