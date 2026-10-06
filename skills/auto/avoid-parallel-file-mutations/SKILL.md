---
name: avoid-parallel-file-mutations
description: Use when making changes to multiple files to prevent concurrent modifications.
---
- Always ensure that only one file is being modified at a time.
- Implement a queuing mechanism for file edits to avoid simultaneous access.
- Check for any ongoing file operations before initiating a new edit.
- Log the status of file operations to track when a file is being edited.
- Use version control to manage changes and avoid conflicts.
- If multiple changes are needed, batch them into a single operation when possible.
- Review the code for any potential race conditions that could lead to parallel modifications.
- Test the file editing logic in isolation to ensure it handles concurrency correctly.