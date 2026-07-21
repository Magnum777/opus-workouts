## Description: <br>
Provides agent-friendly UniFi Network controller tools for listing devices, managing clients and WiFi networks, controlling switch ports and traffic rules, creating guest vouchers, and running raw API requests. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[araa47](https://clawhub.ai/user/araa47) <br>

### License/Terms of Use: <br>


## Use Case: <br>
Network administrators and developers use this skill to let an agent inspect and operate UniFi controllers, including device management, client access control, WiFi administration, switch-port actions, firewall and traffic-rule review, and voucher creation. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: This skill can give an agent broad live control over UniFi network infrastructure. <br>
Mitigation: Use a dedicated least-privileged local account where possible and require explicit approval before mutating actions such as restart, upgrade, block, disable, delete, password-change, PoE, traffic-rule, or raw API commands. <br>
Risk: Controller credentials are stored in environment configuration for the script to use. <br>
Mitigation: Protect the .env file, avoid logging or sharing credentials, and rotate the dedicated account password if it may have been exposed. <br>
Risk: Raw API access and relaxed TLS verification can weaken normal safety boundaries, especially on production networks. <br>
Mitigation: Restrict raw API use, run only against trusted controllers and networks, and avoid production use unless TLS verification and raw API access are tightly controlled. <br>


## Reference(s): <br>
- [ClawHub skill page](https://clawhub.ai/araa47/skills/ez-unifi) <br>


## Skill Output: <br>
**Output Type(s):** [text, JSON, shell commands, configuration, guidance] <br>
**Output Format:** [Markdown guidance with bash commands; script responses are table or JSON output] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires UniFi controller credentials in environment configuration and Python 3.13; live output depends on controller state, network reachability, permissions, and the command invoked.] <br>

## Skill Version(s): <br>
1.0.1 (source: server release metadata) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
