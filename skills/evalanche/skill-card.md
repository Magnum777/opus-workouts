## Description: <br>
Evalanche is a multi-EVM agent wallet skill for onchain identity, x402 payments, cross-chain liquidity, gas funding, perpetual trading, prediction markets, and DeFi operations across EVM and Avalanche networks. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[ijaack](https://clawhub.ai/user/ijaack) <br>

### License/Terms of Use: <br>
MIT-0 <br>


## Use Case: <br>
Developers and agent operators use this skill to equip agents with wallet, MCP, and SDK workflows for balances, transactions, swaps, bridges, staking, market data, prediction markets, and chain management. It is intended for agents that are explicitly allowed to operate crypto wallets and pay network or venue costs. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The skill can sign transactions, trade, bridge, stake, approve spending, withdraw funds, and upgrade contracts. <br>
Mitigation: Install it only for agents that are explicitly allowed to operate funded wallets, and require review for every tool call that can move funds or change contract state. <br>
Risk: Wallet keys or mnemonic material can expose funded accounts if reused or stored on a shared or compromised host. <br>
Mitigation: Use a fresh low-balance wallet or isolated mnemonic, avoid treasury keys, and maintain a plan to rotate or delete the persistent keystore. <br>
Risk: External CLI resolution for Polymarket workflows could execute an unintended binary if PATH is compromised. <br>
Mitigation: Pin the Polymarket CLI path with EVALANCHE_POLYMARKET_CLI_BIN before enabling authenticated Polymarket tools. <br>
Risk: HTTP MCP mode can expose wallet capabilities beyond the local agent boundary if network controls are weak. <br>
Mitigation: Prefer stdio mode where possible; if HTTP mode is used, keep it local and require an authentication token plus host-level access controls. <br>


## Reference(s): <br>
- [Evalanche source and homepage](https://github.com/iJaack/evalanche) <br>
- [ClawHub skill page](https://clawhub.ai/ijaack/skills/evalanche) <br>


## Skill Output: <br>
**Output Type(s):** [Text, Markdown, Code, Shell commands, Configuration, Guidance] <br>
**Output Format:** [Markdown with inline code blocks, shell commands, configuration details, and tool guidance] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [May describe actions that spend funds or submit transactions; review wallet operations before execution.] <br>

## Skill Version(s): <br>
1.12.0 (source: ClawHub release evidence) <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
