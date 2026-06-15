## Description: <br>
Transform Markdown or outlines into polished Word/PDF documents with professional templates. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[harrylabsj](https://clawhub.ai/user/harrylabsj) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers, product teams, and business users use Doc Weaver to convert local Markdown documents or outlines into polished Word and PDF deliverables with template-based formatting. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: Running the local Python conversion script requires installing and trusting document-conversion dependencies such as python-docx, pandoc, and weasyprint. <br>
Mitigation: Install dependencies from trusted sources and run the script in an environment appropriate for local file conversion. <br>
Risk: Converting untrusted Markdown may expose the local pandoc or weasyprint toolchain to unexpected external content processing. <br>
Mitigation: Use explicit input and output paths, review Markdown before conversion, and avoid converting untrusted content unless the local toolchain is isolated. <br>


## Reference(s): <br>
- [Doc Weaver template reference](references/templates.md) <br>
- [Doc Weaver ClawHub page](https://clawhub.ai/harrylabsj/doc-weaver) <br>


## Skill Output: <br>
**Output Type(s):** [text, markdown, code, shell commands, guidance, files] <br>
**Output Format:** [Markdown guidance with shell commands; generated local .docx, .pdf, or preview Markdown files when the script is run.] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Uses local input and output paths, built-in templates, and local document-conversion dependencies.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata and skill.json) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
