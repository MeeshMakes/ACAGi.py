# Changelog

## 2025-12-05
- Enabled dragging desktop icons to external destinations with cleanup when moves leave the Virtual Desktop sandbox.
- Recorded internal drop bookkeeping to keep icon refresh smooth during drag operations.
- Documented design and validation context for the drag/drop synchronization effort.
- Clarified that internal folder moves and grid snaps are tracked as internal drops so the filesystem cleanup only runs for true external moves.
