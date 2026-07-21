## Description: <br>
Creates AI-powered social media images, videos, thumbnails, captions, hashtags, and platform-specific content workflows for TikTok, Instagram, YouTube, and Twitter/X. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[okaris](https://clawhub.ai/user/okaris) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Content creators, social media managers, influencers, and brands use this skill to draft platform-specific prompts and CLI workflows for generating social posts, short-form videos, thumbnails, captions, hashtags, and repurposed campaign assets. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill includes a Twitter/X posting command that could publish generated content as a live public action. <br>
Mitigation: Review all generated text and media before posting, require explicit confirmation before publishing, and use least-privilege credentials for the intended account. <br>
Risk: The skill depends on inference.sh CLI installation and login for external app execution. <br>
Mitigation: Install only if you trust inference.sh and are comfortable with its CLI login session. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/okaris/skills/ai-social-media-content) <br>
- [inference.sh](https://inference.sh) <br>
- [inference.sh CLI checksums](https://dist.inference.sh/cli/checksums.txt) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown guidance with inline shell commands and JSON inputs] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Produces prompts and command examples for external inference.sh apps; generated media or posts require user review before use.] <br>

## Skill Version(s): <br>
0.1.5 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
