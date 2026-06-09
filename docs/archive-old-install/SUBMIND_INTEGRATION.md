# SUBMIND_INTEGRATION.md – Quick Reference for Sub‑Agents

This guide gives sub‑agents a minimal but practical cheat‑sheet for importing and using Nova’s new core systems. It is intentionally terse – sub‑agents should copy‑paste the snippets into their own code or scripts.

---

## 1. Importing Modules

All Nova‑provided capabilities are exposed as top‑level imports from the `openclaw` package. Example (Node/TypeScript):
```ts
import { memory, trading, browser, gmail } from "openclaw";
```
If a capability is not yet available (e.g., Stable Diffusion), the import will throw at runtime; guard it with a try/catch.

---

## 2. Vector Memory (LanceDB)

### Upsert a document
```ts
await memory.upsert({
  id: "doc42",
  vector: [0.12, 0.34, /* … */],
  metadata: { title: "Nova System Overview" },
});
```
### Similarity search
```ts
const results = await memory.search({
  vector: queryEmbedding,
  topK: 5,
  filter: { title: { $contains: "Trading" } },
});
```
### Delete
```ts
await memory.delete("doc42");
```

---

## 3. Trading Bot Daemon

### Start the daemon (usually done once per session)
```ts
await trading.start({
  pairs: ["SOL/USDC"],
  strategy: "mean-reversion",
});
```
### Stop the daemon
```ts
await trading.stop();
```
### Query live P&L
```ts
const pnl = await trading.monitor({ pair: "SOL/USDC" });
console.log(`Current P&L: ${pnl}`);
```

---

## 4. Browser Automation (Playwright)

### Run a script file against a URL
```ts
await browser.run({
  url: "https://mail.google.com",
  script: "./scripts/gmail-login.js",
});
```
**Script example (`gmail-login.js`):**
```js
module.exports = async ({ page }) => {
  await page.fill("input[type=email]", "myemail@example.com");
  await page.click("button:has-text('Next')");
  // …continue with password, 2FA, etc.
};
```
### Inline script (quick one‑liners)
```ts
await browser.run({
  url: "https://example.com",
  script: `async ({page}) => { await page.screenshot({path:'out.png'}); }`,
});
```

---

## 5. Stable Diffusion Control (future stub)

When the skill is installed, the API will match the pattern below. Keep the stub for forward compatibility.
```ts
import { sd } from "openclaw";
await sd.generate({
  prompt: "cyberpunk raccoon",
  size: [1024, 1024],
  controlNet: { type: "depth", weight: 0.8 },
});
```
Wrap calls in `if (sd?.generate) { … }` to avoid crashes before the skill lands.

---

## 6. Gmail Integration

### Send an email
```ts
await gmail.send({
  to: "jamie@example.com",
  subject: "Nova Update",
  body: "The new systems are live.",
});
```
### List recent threads
```ts
const threads = await gmail.list({ maxResults: 10 });
for (const t of threads) console.log(`${t.id}: ${t.snippet}`);
```
### Search mails
```ts
const matches = await gmail.search({ query: "subject:Invoice" });
```

---

## 7. Common Patterns

1. **Guard against missing skills** – wrap imports or calls in `try/catch`.
2. **Idempotency** – most upserts are safe to repeat; they replace existing entries.
3. **Async/await** – all APIs are promise‑based; always `await`.
4. **Logging** – use `console.log` or the built‑in `log` module for debugging; logs are captured in `logs/`.
5. **Error handling** – catch specific errors (`MemoryError`, `TradingError`, etc.) to provide graceful fallback.

```ts
try {
  await memory.upsert(...);
} catch (e) {
  console.error("Memory upsert failed:", e);
  // optional retry or fallback
}
```

---

## 8. Debugging Tips

- **Check daemon status:** `openclaw trading status`
- **Inspect memory:** `openclaw memory inspect --id doc42`
- **Browser logs:** `logs/browser.log`
- **Enable verbose mode:** add `--verbose` to any CLI command.

---

*All snippets assume the relevant skill is installed and the user has performed any required OAuth or API‑key setup.*
