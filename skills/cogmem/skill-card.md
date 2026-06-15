## Description: <br>
Cogmem Memory Backend installs and connects cogmem to an OpenClaw workspace so an agent can store conversation turns and recall prior context using configured embedding and LLM models. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[liuqin164](https://clawhub.ai/user/liuqin164) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and OpenClaw users use this skill to install cogmem, initialize project-scoped memory, configure embedding and LLM models, import existing OpenClaw memory, and verify recall/status for a single-agent workspace. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill records conversation content and reuses stored memory across sessions. <br>
Mitigation: Review the skill before installing, confirm the memory behavior is acceptable, and identify how to disable recording or purge stored memory before use. <br>
Risk: The install flow uses a remote curl-to-bash pattern. <br>
Mitigation: Inspect or pin the installer before execution instead of piping the remote script directly into a shell. <br>
Risk: The published skill version is 2.0.3 while the artifact's install section says it installs cogmem@2.0.2. <br>
Mitigation: Verify the intended cogmem CLI version before installing or updating. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/liuqin164/cogmem-memory-backend) <br>
- [Cogmem project link referenced by artifact](https://github.com/liuqin164/Cogmem) <br>


## Skill Output: <br>
**Output Type(s):** [Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown with bash and TOML code blocks] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Includes commands that may modify the local OpenClaw workspace and cogmem configuration.] <br>

## Skill Version(s): <br>
2.0.3 (source: server release metadata and SKILL.md frontmatter) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
