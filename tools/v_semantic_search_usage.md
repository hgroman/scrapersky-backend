# Semantic Search Usage Guide

## Quick Reference

### Basic Command
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "your search query"
```

## Command Line Options

| Option | Values | Description |
|--------|--------|-------------|
| `--mode` | `titles`, `full` | `titles` = show document titles only, `full` = show full content |
| `--limit` | integer | Number of results to return (default: 10) |
| `--threshold` | float | Similarity threshold (0.0-1.0) |
| `--filter` | JSON string | Metadata filtering |
| `--format` | `text`, `json` | Output format |

## Common Usage Examples

### Search for titles only (fast)
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "workflow sitemap analysis" --mode titles --limit 5
```

### Search for full content (detailed)
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "scraper api configuration" --mode full --limit 3
```

### High similarity threshold
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "database schema" --threshold 0.8
```

### JSON output for scripting
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "authentication" --format json
```

## Search Query Tips

- **Use specific terms:** "WF4 sitemap analysis" vs "workflow"
- **Include context:** "scraper api integration" vs "api"
- **Technical terms work well:** "SQLAlchemy ORM patterns", "FastAPI router"
- **Workflow references:** "WF4", "WF5", "domain curation"

## Common Searches

### Find workflow documentation
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 domain curation workflow" --mode titles
```

### Find API integration patterns
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "scraper api client usage" --mode full --limit 2
```

### Find architectural guidelines
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "ORM requirements architectural principles" --mode full
```

### Debug specific components
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "sitemap analyzer implementation" --mode full
```

## Vector Database Info

- **Database:** Supabase `project_docs` table
- **Embeddings:** OpenAI text-embedding-ada-002
- **Documents:** Automatically indexed from project documentation
- **Registry:** Managed via `Docs/Docs_19_File-2-Vector-Registry-System/` scripts

## Troubleshooting

### Command not found
Make sure you're in the project root directory:
```bash
cd /Users/henrygroman/development/python-projects/ScraperSky-Back-End-WorkSpace/scraper-sky-backend
```

### No results
- Try broader search terms
- Lower the threshold: `--threshold 0.6`
- Check if documents are indexed in the vector database

### Environment variables required
- `OPENAI_API_KEY`
- `SUPABASE_URL` 
- `SUPABASE_SERVICE_ROLE_KEY`

## Integration with AI Assistants

When asking AI to search semantically:
```
"Search for workflow documentation using semantic search with the query 'WF4 sitemap analysis'"
```

The AI should use:
```bash
python Docs/Docs_18_Vector_Operations/Scripts/semantic_query_cli.py "WF4 sitemap analysis" --mode titles --limit 5
```