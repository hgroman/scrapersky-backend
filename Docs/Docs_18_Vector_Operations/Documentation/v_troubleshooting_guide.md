# Vector Database Troubleshooting Guide

This guide provides quick solutions for common issues encountered with the ScraperSky Vector Database.

## Troubleshooting Cheatsheet

| Symptom           | Likely Cause                     | Fast Fix                                     |
|-------------------|----------------------------------|----------------------------------------------|
| `Similarity: nan` | Un-normalized embeddings         | Re-run fix script (see `v_nan_issue_resolution.md`). |
| `pg_net` errors   | Extension missing or permissions | `CREATE EXTENSION IF NOT EXISTS pg_net;` Grant usage if needed. |
| No results        | Threshold too high or null embeddings | Lower search threshold / run null-embedding scan. |
| API fails         | Key revoked or quota hit         | Rotate key; monitor status.openai.com.       |
| Connection Errors | Incorrect `DATABASE_URL`, firewall, or service down | Verify `DATABASE_URL`, check network, Supabase status. |
| Permission Denied | DB user permissions insufficient | Review and grant necessary role privileges.  |
