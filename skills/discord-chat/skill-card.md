## Description: <br>
Send messages, reply to messages, and search message history in Discord channels using the message tool. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[bowenqt](https://clawhub.ai/user/bowenqt) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers and operators use this skill to communicate through Discord, review channel activity, search message history, and manage channels through a configured Discord bot. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Discord bot actions can send public messages or change channel state when granted broad permissions. <br>
Mitigation: Install only for a Discord bot and server you control, grant minimum required permissions, and require explicit confirmation before public, destructive, or channel-management actions. <br>
Risk: Discord bot tokens and webhook secrets can be exposed through configuration mistakes. <br>
Mitigation: Store tokens in environment variables or a secret manager, avoid committing secrets, and rotate any exposed token immediately. <br>


## Reference(s): <br>
- [Discord Chat Skill Page](https://clawhub.ai/bowenqt/skills/discord-chat) <br>
- [Discord Developer Portal](https://discord.com/developers/applications) <br>
- [Discord API Docs](https://discord.com/developers/docs) <br>
- [Discord Permissions Documentation](https://discord.com/developers/docs/topics/permissions) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown with inline shell command examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces message-tool commands and operational guidance for Discord bot interactions.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
