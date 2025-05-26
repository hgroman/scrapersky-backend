# DART MCP Integration Guide

This guide provides comprehensive information on using the DART Model Context Protocol (MCP) server integration within the ScraperSky project. It is intended for the AI pairing partner (Cascade) to effectively manage tasks and documents in DART.

## 1. Introduction

The DART MCP server allows programmatic access to your DART workspace, enabling creation, retrieval, update, and deletion of tasks and documents. This integration streamlines project management and collaboration.

## 2. Setup and Verification

The DART MCP server is configured in Windsurf's `mcp_config.json`. The `DART_TOKEN` environment variable is essential for authentication.

**Verifying Connection:**
A simple way to verify the connection is to list tasks:
```xml
<mcp0_list_tasks>{"limit": 1}</mcp0_list_tasks>
```
If this returns a task, the connection is active.

**Identifying Dartboards (Workspaces):**
Dartboards are DART's equivalent of workspaces or projects.
*   Currently identified dartboards (based on tasks seen so far):
    *   `General/Tasks`
    *   `Personal/Tutorial tasks`
*   To find all dartboards associated with tasks, list a larger number of tasks and observe the `dartboard` field:
    ```xml
    <mcp0_list_tasks>{"limit": 100}</mcp0_list_tasks>
    ```
*   The `mcp0_get_config` tool should ideally provide a list of all dartboards, but it has been returning an "Arguments are required" error. If this is resolved, it's the preferred method:
    ```xml
    <mcp0_get_config>{}</mcp0_get_config>
    ```

## 3. Available DART MCP Tools

Below is a list of available tools for interacting with DART. All tools expect arguments as a JSON object and return JSON responses.

### 3.1. General Configuration

*   **`mcp0_get_config`**: Get information about the user's space.
    *   **Description**: Retrieves available assignees, dartboards, folders, statuses, tags, priorities, and sizes.
    *   **Arguments**: `{}` (Note: Has been problematic, may require a dummy argument if errors persist, e.g., `{"_comment": "fetching config"}`)
    *   **Example**: `<mcp0_get_config>{}</mcp0_get_config>`

### 3.2. Task Management Tools

*   **`mcp0_list_tasks`**: List tasks.
    *   **Description**: Lists tasks with optional filtering.
    *   **Arguments**:
        *   `dartboard` (string): **CRITICAL PARAMETER** - Filter by dartboard title. While technically optional, this parameter is practically required for effective task retrieval. Without specifying a dartboard, results may be incomplete or empty even when tasks exist.
        *   `limit` (integer): Number of results per page.
        *   `offset` (integer): Initial index for pagination.
        *   `status` (string): Filter by status.
        *   `assignee` (string): Filter by assignee name or email.
        *   `priority` (string): Filter by priority.
        *   (See tool schema for all available filters)
    *   **Example (List 5 tasks from "General/Tasks")**: `<mcp0_list_tasks>{"dartboard": "General/Tasks", "limit": 5}</mcp0_list_tasks>`
    *   **IMPORTANT**: Always specify the `dartboard` parameter (e.g., "General/Tasks") when listing tasks to ensure complete results.

*   **`mcp0_create_task`**: Create a new task.
    *   **Description**: Creates a new task with specified properties.
    *   **Arguments (Required)**:
        *   `title` (string): The title of the task.
    *   **Arguments (Optional)**:
        *   `description` (string): Longer description (supports Markdown).
        *   `dartboard` (string): Title of the dartboard.
        *   `status` (string): Task status (e.g., "To-do", "Doing", "Done").
        *   `priority` (string): Task priority (e.g., "High", "Medium", "Low").
        *   `assignee` (string): Assignee name or email.
        *   `tags` (array of strings): Tags to apply.
        *   (See tool schema for all available properties)
    *   **Example**: `<mcp0_create_task>{"title": "Develop new feature", "dartboard": "General/Tasks", "description": "Implement X, Y, and Z.", "priority": "High"}</mcp0_create_task>`

*   **`mcp0_get_task`**: Retrieve an existing task.
    *   **Description**: Gets detailed information for a specific task by its ID.
    *   **Arguments (Required)**:
        *   `id` (string): The 12-character alphanumeric ID of the task.
    *   **Example**: `<mcp0_get_task>{"id": "tIIKo8GaHIq1"}</mcp0_get_task>`

*   **`mcp0_update_task`**: Update an existing task.
    *   **Description**: Modifies properties of an existing task.
    *   **Arguments (Required)**:
        *   `id` (string): The ID of the task to update.
    *   **Arguments (Modifiable)**: Any property available in `create_task` (e.g., `title`, `description`, `status`, `priority`, `assignee`, `tags`).
    *   **Example (Mark task as "Done")**: `<mcp0_update_task>{"id": "tIIKo8GaHIq1", "status": "Done"}</mcp0_update_task>`

*   **`mcp0_delete_task`**: Delete a task.
    *   **Description**: Moves a task to the trash (recoverable).
    *   **Arguments (Required)**:
        *   `id` (string): The ID of the task to delete.
    *   **Example**: `<mcp0_delete_task>{"id": "tIIKo8GaHIq1"}</mcp0_delete_task>`

### 3.3. Document Management Tools

*   **`mcp0_list_docs`**: List documents.
    *   **Description**: Lists documents with optional filtering.
    *   **Arguments (Optional)**:
        *   `limit` (integer): Number of results per page.
        *   `offset` (integer): Initial index for pagination.
        *   `folder` (string): Filter by folder title.
        *   `title` (string): Filter by document title.
        *   (See tool schema for all available filters)
    *   **Example**: `<mcp0_list_docs>{"limit": 10}</mcp0_list_docs>`

*   **`mcp0_create_doc`**: Create a new document.
    *   **Description**: Creates a new document.
    *   **Arguments (Required)**:
        *   `title` (string): The title of the document.
    *   **Arguments (Optional)**:
        *   `text` (string): Text content (supports Markdown).
        *   `folder` (string): Title of the folder to place the doc in.
    *   **Example**: `<mcp0_create_doc>{"title": "Project Specification", "text": "# Section 1\nDetails...", "folder": "Project Docs"}</mcp0_create_doc>`

*   **`mcp0_get_doc`**: Retrieve an existing document.
    *   **Description**: Gets detailed information for a specific document by its ID.
    *   **Arguments (Required)**:
        *   `id` (string): The 12-character alphanumeric ID of the document.
    *   **Example**: `<mcp0_get_doc>{"id": "docIdExample"}</mcp0_get_doc>`

*   **`mcp0_update_doc`**: Update an existing document.
    *   **Description**: Modifies properties of an existing document.
    *   **Arguments (Required)**:
        *   `id` (string): The ID of the document to update.
    *   **Arguments (Modifiable)**: `title`, `text`, `folder`.
    *   **Example**: `<mcp0_update_doc>{"id": "docIdExample", "text": "Updated content."}</mcp0_update_doc>`

*   **`mcp0_delete_doc`**: Delete a document.
    *   **Description**: Moves a document to the trash (recoverable).
    *   **Arguments (Required)**:
        *   `id` (string): The ID of the document to delete.
    *   **Example**: `<mcp0_delete_doc>{"id": "docIdExample"}</mcp0_delete_doc>`

## 4. Common Workflows

**Workflow: Create a Task for a New Feature and an Associated Design Document**

1.  **Create the design document:**
    ```xml
    <mcp0_create_doc>{"title": "Feature X Design Spec", "text": "## Overview\n...", "folder": "Design Documents"}</mcp0_create_doc>
    ```
    *(Assume this returns an ID like `docNewFeatureSpec123`)*

2.  **Create the task, linking the document in the description:**
    ```xml
    <mcp0_create_task>{"title": "Implement Feature X", "dartboard": "General/Tasks", "description": "Implement Feature X as per design spec: [Feature X Design Spec](https://app.itsdart.com/d/docNewFeatureSpec123) (replace with actual URL if available from get_doc or UI)", "priority": "High"}</mcp0_create_task>
    ```

## 5. Troubleshooting

*   **Missing or incomplete task results when using `mcp0_list_tasks`**:
    *   The most common cause is not specifying the `dartboard` parameter. Always include `"dartboard": "General/Tasks"` (or other appropriate dartboard name) in your query.
    *   Ensure you are using the correct string value for the `status` parameter. Valid status strings can be found by using the `mcp0_get_config` tool: `<mcp0_get_config>{}</mcp0_get_config>`.
    *   If you're uncertain which dartboard contains your tasks, list all tasks with a high limit and observe the dartboard field: `<mcp0_list_tasks>{"limit": 100}</mcp0_list_tasks>`

*   **Error: "Arguments are required (Code -32603)" for `mcp0_get_config`**:
    *   This tool is documented to work with empty arguments (`{}`). If the error persists, the DART MCP server might have a bug or undocumented requirement.
    *   Workaround for finding dartboards: Use `mcp0_list_tasks` with a high limit and extract unique `dartboard` values.
    *   For other config data (assignees, statuses), if `mcp0_get_config` remains unusable, these might need to be inferred from existing tasks/docs or provided manually.

*   **Task/Doc Not Found**:
    *   Double-check the 12-character ID.
    *   Ensure the item hasn't been permanently deleted (trash is recoverable).

*   **Permissions Issues**:
    *   Ensure the `DART_TOKEN` used in `mcp_config.json` has the necessary permissions for the actions being attempted.

---
This guide should be updated as new information becomes available or if the behavior of the DART MCP server tools changes.
