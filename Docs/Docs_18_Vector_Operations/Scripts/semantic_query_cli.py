#!/usr/bin/env python
"""
Performs an end-to-end semantic search.
Accepts a text query, generates an OpenAI embedding, and uses it to query
the Supabase database via an RPC call to a function that accepts a native vector.

Supports metadata filtering and structured JSON output.
"""

import asyncio
import os
import sys
import argparse
import logging
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAIError
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
EMBEDDING_MODEL = "text-embedding-ada-002"

# Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY"
)  # Using service role for server-side script
DB_FUNCTION_NAME = "perform_semantic_search_direct"


def check_env_vars():
    """Checks for required environment variables and returns False if any are missing."""
    required_vars = {
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_KEY": SUPABASE_KEY,
    }
    missing_vars = [key for key, value in required_vars.items() if not value]
    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        return False
    return True


async def get_openai_embedding(text: str, client: AsyncOpenAI) -> list[float] | None:
    """Generates an embedding for the given text using OpenAI's API."""
    if not text:
        logger.error("Input text for embedding cannot be empty.")
        return None
    try:
        processed_text = text.replace("\n", " ")
        logger.info(f'Requesting embedding for text: "{processed_text[:100]}..."')
        response = await client.embeddings.create(
            input=[processed_text], model=EMBEDDING_MODEL
        )
        embedding = response.data[0].embedding
        logger.info(
            f"Embedding received successfully with {len(embedding)} dimensions."
        )
        return embedding
    except OpenAIError as e:
        logger.error(f"OpenAI API error while generating embedding: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred during embedding generation: {e}")
        return None


async def perform_db_search(
    supabase_client: Client,
    embedding: list[float],
    limit: int,
    threshold: float,
    metadata_filter: dict,
) -> list[dict] | None:
    """Performs semantic search by calling the database RPC function."""
    if not embedding:
        logger.error("Cannot perform search with an empty embedding vector.")
        return None
    try:
        params = {
            "query_embedding_param": embedding,
            "match_count_param": limit,
            "match_threshold_param": threshold,
            "metadata_filter_param": metadata_filter,
        }
        logger.info(
            f"Executing RPC call to '{DB_FUNCTION_NAME}' with filter: {metadata_filter}"
        )

        response = await asyncio.to_thread(
            supabase_client.rpc(DB_FUNCTION_NAME, params).execute
        )

        logger.info("RPC call executed successfully.")
        return response.data
    except Exception as e:
        logger.error(f"An error occurred during database search: {e}")
        if hasattr(e, "message"):
            logger.error(f"Database error message: {e.message}")
        return None


async def main():
    parser = argparse.ArgumentParser(
        description="Perform semantic search on the database."
    )
    parser.add_argument("query_text", type=str, help="The text to search for.")
    parser.add_argument(
        "--mode",
        type=str,
        choices=["titles", "full"],
        default="full",
        help="Output mode for text format: titles or full content.",
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Number of results to return."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.7,
        help="Similarity threshold for matching.",
    )
    parser.add_argument(
        "--filter",
        type=str,
        default="{}",
        help='JSON string for metadata filtering (e.g., \'{"key": "value"}\').',
    )
    parser.add_argument(
        "--format",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format: text or json.",
    )

    args = parser.parse_args()

    try:
        metadata_filter = json.loads(args.filter)
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON provided for --filter argument: {args.filter}")
        sys.exit(1)

    if not check_env_vars():
        sys.exit(1)

    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
    supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    embedding_vector = await get_openai_embedding(args.query_text, openai_client)
    if not embedding_vector:
        logger.error("Halting execution due to embedding failure.")
        return

    search_results = await perform_db_search(
        supabase_client, embedding_vector, args.limit, args.threshold, metadata_filter
    )

    if search_results is not None:
        logger.info(f"Search returned {len(search_results)} results.")
        if args.format == "json":
            print(json.dumps(search_results, indent=2))
        else:  # 'text' format
            print("\n--- Semantic Search Results ---")
            if not search_results:
                print("No results found matching the criteria.")
            elif args.mode == "full":
                for item in search_results:
                    print(f"\n{'=' * 20}")
                    print(f"ID: {item['id']}")
                    print(f"Title: {item['title']}")
                    print(f"Similarity: {item['similarity']:.4f}")
                    print(f"--- Content ---")
                    print(item["content"])
                    print(f"{'=' * 20}\n")
            elif args.mode == "titles":
                for item in search_results:
                    print(
                        f"- ID: {item['id']}, Similarity: {item['similarity']:.4f}, Title: {item['title']}"
                    )
    else:
        logger.error("Search failed. Check logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Critical error in script execution: {e}")
        print(f"Critical error: {e}", file=sys.stderr)
        sys.exit(1)
