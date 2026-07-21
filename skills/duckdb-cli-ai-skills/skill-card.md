## Description: <br>
DuckDB CLI specialist for SQL analysis, data processing, and file conversion across CSV, Parquet, JSON, and database workflows. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[camelsprout](https://clawhub.ai/user/camelsprout) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers and data practitioners use this skill to have an agent propose DuckDB CLI commands, SQL examples, output-format choices, and configuration guidance for local data analysis and file conversion. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Generated DuckDB commands may read broad file globs or write to unintended export paths. <br>
Mitigation: Review file globs, COPY targets, .output and .once destinations before running generated commands. <br>
Risk: Generated SQL may mutate a database through CREATE or INSERT statements. <br>
Mitigation: Use read-only mode when inspecting existing databases and review mutating SQL before execution. <br>
Risk: Editor-based workflows may open local files or execute editor behavior outside the agent response. <br>
Mitigation: Review .edit/editor use and environment-selected editors before applying generated workflows. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/camelsprout/skills/duckdb-cli-ai-skills) <br>
- [DuckDB CLI Overview](https://duckdb.org/docs/stable/clients/cli/overview) <br>
- [DuckDB CLI Arguments](https://duckdb.org/docs/stable/clients/cli/arguments) <br>
- [DuckDB CLI Dot Commands](https://duckdb.org/docs/stable/clients/cli/dot_commands) <br>
- [DuckDB CLI Output Formats](https://duckdb.org/docs/stable/clients/cli/output_formats) <br>
- [DuckDB CLI Editing](https://duckdb.org/docs/stable/clients/cli/editing) <br>
- [DuckDB CLI Autocomplete](https://duckdb.org/docs/stable/clients/cli/autocomplete) <br>
- [DuckDB CLI Syntax Highlighting](https://duckdb.org/docs/stable/clients/cli/syntax_highlighting) <br>
- [DuckDB CLI Safe Mode](https://duckdb.org/docs/stable/clients/cli/safe_mode) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown guidance with SQL and bash command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Includes DuckDB CLI flags, SQL snippets, data conversion examples, and safety guidance such as read-only or safe mode where applicable.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
