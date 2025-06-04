# Document Registry Getting Started

This short guide demonstrates how to use the conversation-driven workflow for document scanning and vectorization.

## 1. Starting the Conversation

Begin by asking me (Cascade) to review a specific directory:

```
You: "Let's review the documents in Docs_10_Final_Audit for vectorization candidates."
```

## 2. Reviewing and Marking Documents

I'll analyze the directory and we'll select documents together:

```
Me: [Lists files in the directory]
"Found 5 markdown files in Docs_10_Final_Audit:
1. audit_results.md 
2. compliance_report.md
3. technical_debt.md
4. user_feedback.md
5. performance_metrics.md"

You: "Let's mark #1 and #3 for vectorization."
```

I'll add the `v_` prefix to these files, following our naming convention:

```
Me: "Added v_ prefix to:
- audit_results.md → v_audit_results.md 
- technical_debt.md → v_technical_debt.md"
```

## 3. Approving the Directory

Once we've marked important documents with `v_`, we'll approve the directory:

```
You: "Approve Docs_10_Final_Audit for scanning."

Me: "Directory Docs_10_Final_Audit approved for scanning."
```

## 4. Updating the Registry

Now we'll update the document registry with only the approved directory:

```
You: "Update the document registry."

Me: [Runs script to scan approved directories]
"Registry updated. Found 2 new vectorization candidates."
```

## 5. Checking Status and Vectorizing

Finally, we'll check what needs to be vectorized and process it:

```
You: "Show me the registry status."

Me: [Shows status report]
"2 documents pending vectorization: v_audit_results.md, v_technical_debt.md"

You: "Vectorize the pending documents."

Me: [Runs vectorization]
"Documents successfully vectorized and registry updated."
```

## The Control is Yours

This workflow gives you complete control:

1. **You decide** which directories to review
2. **You decide** which documents to mark with `v_`
3. **You decide** when to approve directories for scanning
4. **You decide** when to update the registry
5. **You decide** when to vectorize documents

No automatic scanning, no mess to clean up - just systematic, controlled document management.

Next time you return to this project, just ask me to continue our systematic review of directories.
