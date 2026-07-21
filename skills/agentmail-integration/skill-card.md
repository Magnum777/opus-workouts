## Description: <br>
Integrates the AgentMail API so agents can create and manage inboxes, send and receive email, and handle webhook-driven email workflows. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[synesthesia-wav](https://clawhub.ai/user/synesthesia-wav) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and agent builders use this skill to connect agents to AgentMail for inbox provisioning, outbound messages, inbound mail checks, and webhook-based email automation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can enable high-impact email actions such as sending messages, forwarding content, managing inboxes, and configuring webhooks. <br>
Mitigation: Require approval before outbound replies or forwarding, avoid bulk or unsolicited sending, and grant AgentMail authority only for intended workflows. <br>
Risk: Incoming email and webhook payloads can contain prompt injection attempts or malicious instructions. <br>
Mitigation: Use sender allowlists, content filtering, untrusted-context prompts, human review for suspicious messages, and trusted webhook endpoints. <br>
Risk: Downloaded email attachments may be unsafe or may overwrite unexpected paths if saved carelessly. <br>
Mitigation: Save attachments only to a restricted directory, sanitize filenames, and scan files before opening or processing them. <br>


## Reference(s): <br>
- [AgentMail API Reference](references/API.md) <br>
- [Webhook Setup and Security](references/WEBHOOKS.md) <br>
- [AgentMail Common Patterns](references/patterns.md) <br>
- [AgentMail Examples](references/EXAMPLES.md) <br>
- [AgentMail Console](https://console.agentmail.to) <br>
- [ClawHub Skill Release](https://clawhub.ai/synesthesia-wav/skills/agentmail-integration) <br>


## Skill Output: <br>
**Output Type(s):** [Guidance, Code, Shell commands, Configuration] <br>
**Output Format:** [Markdown guidance with Python code examples and shell commands] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires AGENTMAIL_API_KEY and the AgentMail Python SDK for live API operations.] <br>

## Skill Version(s): <br>
1.1.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
