## Description: <br>
Memory Hygiene audits, cleans, and optimizes Clawdbot's LanceDB vector memory when memory is bloated, token usage is high from irrelevant auto-recalls, or memory maintenance automation is needed. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[dylanbaker24](https://clawhub.ai/user/dylanbaker24) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and Clawdbot operators use this skill to audit vector memory, remove unwanted LanceDB memory data, reseed selected facts, and configure memory capture behavior. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Wipe instructions can permanently delete Clawdbot vector memory. <br>
Mitigation: Back up or export memory, confirm the target path, and keep a rollback plan before running wipe commands. <br>
Risk: Monthly maintenance automation can repeatedly reset memory without direct review. <br>
Mitigation: Use cron-based maintenance only when recurring unattended resets are acceptable; otherwise run maintenance manually. <br>
Risk: Reseeding can omit important facts or reintroduce sensitive material. <br>
Mitigation: Review source facts before storing them, keep each memory concise, and avoid OAuth URLs, tokens, raw logs, and transient status messages. <br>


## Reference(s): <br>
- [Memory Hygiene ClawHub page](https://clawhub.ai/dylanbaker24/skills/memory-hygiene) <br>
- [Declared homepage](https://github.com/xdylanbaker/memory-hygiene) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Shell commands, Configuration] <br>
**Output Format:** [Markdown with inline shell and JSON code blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Includes wipe and cron examples that should be reviewed before execution.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
