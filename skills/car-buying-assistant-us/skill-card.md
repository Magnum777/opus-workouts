## Description:
A US-market fork of the Canadian car-buying-assistant skill. Adds VIN decoding, state-specific OTD pricing, dealer email pattern matching, and negotiation templates for the US auto market. Helps buyers research, compare, and negotiate on new/used vehicles without sending money or payment details. <br>

## Publisher:
Nova / Layered Media LLC <br>

### License/Terms of Use:
MIT-0 (forked from justintsmith/car-buying-assistant under MIT-0) <br>

## Use Case:
External users and agent operators use this skill to research US car listings, compare candidates, identify red flags, calculate out-the-door prices for any state, find dealer staff emails, and prepare negotiation drafts while keeping purchase decisions and seller contact under user control. <br>

### Deployment Geography for Use:
United States <br>

## Known Risks and Mitigations:
Risk: Email pattern matcher generates probable addresses; these are guesses, not verified. <br>
Mitigation: Always verify email addresses before sending. Use bounce detection or domain confirmation. <br>
Risk: OTD calculator uses average state/local tax rates; actual rates vary by county and city. <br>
Mitigation: Use as an estimate only. Confirm actual tax rate with dealer or DMV. <br>
Risk: Seller message drafts could include inaccurate, incomplete, or sensitive information if sent without review. <br>
Mitigation: Review every draft before sending and avoid including payment details, SSN, banking info, or full home address. <br>

## Reference(s):
- [Original skill](https://clawhub.ai/justintsmith/car-buying-assistant) by justintsmith <br>
- [NHTSA vPIC API](https://vpic.nhtsa.dot.gov/api/) for VIN decoding <br>
- [NADA state fee guide](https://www.nada.org/) for fee benchmarks <br>

## Skill Output:
**Output Type(s):** [text, markdown, JSON, email drafts, call sheets] <br>
**Output Format:** [Markdown reports, JSON listing data, email drafts, printable call sheets] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** Writes car-search session files under ~/.openclaw/workspace/car-search/ when used as directed. <br>

## Skill Version(s):
1.0.0 <br>

## Ethical Considerations:
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. Never send money, payment details, or personal information via generated drafts without explicit user review. <br>
