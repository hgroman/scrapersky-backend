1. High-level Overview (for you right now)

First we permanently delete every orphaned, duplicate, and confusing enum type from the database (8+ types gone forever).
Then we atomically rename every model, scheduler, service, and relevant router to perfectly match the 7 workflows (WF1, WF2, WF3, WF4, WF5, no WF6, WF7).
Everything is done in two phases so production never breaks.
After this, any human or AI looking at the file tree instantly knows exactly which workflow a file belongs to.

Below are the three ready-to-save markdown files.
────────────────────────────────────────