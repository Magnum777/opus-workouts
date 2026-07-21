## Description: <br>
Sends email through Resend's HTTPS API with a zero-dependency Node.js script that defaults to dry-run and requires explicit send flags, an API key, and a recipient allowlist for real email. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[jwestburg](https://clawhub.ai/user/jwestburg) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and operators use this skill to draft, review, dry-run, and, after explicit approval, send outbound email through a Resend account from Node.js without OAuth or dependencies. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can send real external email when explicitly invoked with credentials. <br>
Mitigation: Keep the default dry-run flow, require exact user approval before adding --send, and enforce RESEND_ALLOWED_TO for all real recipients. <br>
Risk: Dry-run logs include the full message body and may expose sensitive reviewed content if shared. <br>
Mitigation: Review dry-run output locally, avoid sending raw transcripts or private workspace context, and redact dry-run logs before sharing them. <br>
Risk: A timeout or network error after a send attempt may leave delivery status ambiguous. <br>
Mitigation: Check the Resend dashboard before retrying to avoid duplicate messages. <br>


## Reference(s): <br>
- [Resend](https://resend.com) <br>
- [Resend Domains](https://resend.com/domains) <br>
- [Resend Pricing](https://resend.com/pricing) <br>
- [ClawHub skill page](https://clawhub.ai/jwestburg/skills/resend-send-native-node) <br>


## Skill Output: <br>
**Output Type(s):** [Shell commands, Configuration, Text, JSON] <br>
**Output Format:** [Markdown guidance with inline shell commands; the script emits plain-text status messages or JSON receipts.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Dry-runs include the reviewed message payload, body byte count, and SHA-256 body hash; successful real sends include a Resend message ID.] <br>

## Skill Version(s): <br>
1.0.15 (source: frontmatter and server release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
