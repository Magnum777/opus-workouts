## Description: <br>
Upload videos, photos, text, and documents to supported social platforms through the Upload-Post API, with support for scheduling, analytics, upload history, and FFmpeg media processing. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[victorcavero14](https://clawhub.ai/user/victorcavero14) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Developers, operators, and social media teams use this skill to prepare Upload-Post API requests for publishing, scheduling, editing, canceling, checking status, retrieving analytics, and processing media across connected social accounts. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can guide publish, schedule, edit, and cancel operations across connected social accounts. <br>
Mitigation: Require explicit review of the exact content, files, destination platforms, visibility settings, profile, schedule, and job_id before any publish, edit, or cancel request. <br>
Risk: Upload-Post API keys and connected social accounts can provide access to uploaded content and posting capabilities. <br>
Mitigation: Use a limited or dedicated profile and API key, protect secrets from logs and prompts, and rotate keys if exposure is suspected. <br>
Risk: FFmpeg processing can transform uploaded media and may produce unexpected output if commands or files are wrong. <br>
Mitigation: Review source files, FFmpeg command strings, output formats, and processed media before publishing or distributing generated results. <br>


## Reference(s): <br>
- [Upload-Post API Documentation](https://docs.upload-post.com) <br>
- [Upload-Post LLM-Friendly Documentation](https://docs.upload-post.com/llm.txt) <br>
- [Platform-Specific Parameters](references/platforms.md) <br>
- [Media Requirements by Platform](references/requirements.md) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown with API parameters, JSON examples, and curl commands] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Outputs may include API endpoints, authentication headers, platform-specific parameters, scheduling fields, status checks, analytics requests, and FFmpeg command examples.] <br>

## Skill Version(s): <br>
1.0.0 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
