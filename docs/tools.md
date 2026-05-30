# Tools

Tools are the bridge between reasoning and action.

Initial tool goals:

* typed tool schemas
* registry
* permission levels
* audit logs
* filesystem read tool
* guarded shell command tool

Current implementation:

* `current_time` returns the current local timestamp.
* `list_directory` lists entries under the project root.
* `read_file` reads text files under the project root.
* `project_status` returns the current git branch and short status.

Safety constraints:

* tools are explicit CLI commands for now, not automatic model actions
* file paths cannot escape the project root
* `.env`, `.env.*`, and generated database files are blocked from `read_file`
* all current tools are read-only

CLI:

```text
/tools
/tool current_time
/tool list_directory path=.
/tool read_file path=README.md
/tool project_status
```
