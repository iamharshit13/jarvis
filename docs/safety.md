# Safety

J.A.R.V.I.S. should use explicit permissions, audit logs, memory controls, and sandboxed tool execution wherever possible.

Early safety priorities:

* no destructive local actions without confirmation
* no secret logging
* clear tool call records
* human approval before irreversible actions

## Repository Hygiene

Private local configuration belongs in `.env`, which must not be committed. Keep real API keys, local tokens, generated databases, logs, and personal machine paths out of tracked files.

Tracked examples should use empty or obviously fake values only.
