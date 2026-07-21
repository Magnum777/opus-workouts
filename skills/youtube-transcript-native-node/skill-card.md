## Description: <br>
Extract a clean plain-text transcript from existing YouTube captions - native Node.js, zero npm dependencies. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jwestburg](https://clawhub.ai/user/jwestburg) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
External users and developers use this skill to extract existing YouTube captions as clean transcript text for summarization, search, quote extraction, timestamped notes, or JSON handoff. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill runs the local yt-dlp binary against user-provided YouTube URLs, creating a local binary supply-chain trust boundary. <br>
Mitigation: Install only if the local yt-dlp source and PATH location are trusted; review the yt-dlp installation path before use. <br>
Risk: Using yt-dlp on private or client-sensitive videos may disclose access patterns to YouTube or process sensitive third-party content. <br>
Mitigation: Avoid private or client-sensitive videos unless that access is appropriate and authorized. <br>
Risk: Extracted captions may be third-party copyrighted content and auto-generated captions may be inaccurate. <br>
Mitigation: Prefer summaries and brief quotes, respect platform terms and rights, and note auto-generated caption uncertainty when known. <br>


## Reference(s): <br>
- [YouTube Transcript Contract](references/youtube-transcript-contract.md) <br>
- [ClawHub Skill Page](https://clawhub.ai/jwestburg/skills/youtube-transcript-native-node) <br>
- [Publisher Profile](https://clawhub.ai/user/jwestburg) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, configuration, guidance] <br>
**Output Format:** [Plain text transcript, timestamped text, JSON transcript object, or concise Markdown guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May identify auto-generated captions when known; refuses transcripts larger than 2,000,000 characters.] <br>

## Skill Version(s): <br>
1.1.5 (source: frontmatter and server-resolved release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
