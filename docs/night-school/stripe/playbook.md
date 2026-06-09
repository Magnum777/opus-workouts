# Stripe Integration Playbook

## Overview

Stripe API integration for the AI Co-Founder Stack product. Enables invoicing, payments, and subscription management for the autonomous AI business assistant.

## Quick Start

### 1. Get API Keys
- Sign up at stripe.com
- Go to Dashboard → Developers → API keys
- **Secret Key** (sk_test_xxx) - Server-side only
- **Publishable Key** (pk_test_xxx) - Client-side

### 2. Install Library
```bash
npm install stripe
pip install stripe
```

### 3. Initialize Client
```javascript
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
```

```python
import stripe
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
```

## Core Use Cases

### Create Customer
```javascript
const customer = await stripe.customers.create({
  name: 'Acme Corp',
  email: 'billing@acme.com',
  description: 'AI Co-Founder Pro Subscriber'
});
// Store customer.id in your database
```

### Create Product & Price
```javascript
// Create product
const product = await stripe.products.create({
  name: 'AI Co-Founder Pro'
});

// Create price (subscription)
const price = await stripe.prices.create({
  product: product.id,
  unit_amount: 7900, // $79.00 in cents
  currency: 'usd',
  recurring: { interval: 'month' }
});
```

### Create Invoice
```javascript
const invoice = await stripe.invoices.create({
  customer: customerId,
  collection_method: 'send_invoice',
  days_until_due: 30
});

// Add line item
await stripe.invoiceItems.create({
  customer: customerId,
  price: priceId,
  invoice: invoice.id
});

// Finalize and send
await stripe.invoices.finalizeInvoice(invoice.id);
await stripe.invoices.sendInvoice(invoice.id);
```

### Handle Webhooks (Critical)
```javascript
const endpoint = stripe.webhookEndpoints.create({
  url: 'https://your-domain.com/webhook',
  enabled_events: [
    'invoice.paid',
    'invoice.payment_failed',
    'customer.subscription.updated',
    'customer.subscription.deleted'
  ]
});

// Webhook handler
app.post('/webhook', express.raw({type: 'application/json'}), (req, res) => {
  const sig = req.headers['stripe-signature'];
  let event;
  
  try {
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
  
  switch (event.type) {
    case 'invoice.paid':
      // Grant access, update database
      const invoice = event.data.object;
      console.log('Invoice paid:', invoice.id);
      break;
    case 'invoice.payment_failed':
      // Revoke access, notify user
      break;
    case 'customer.subscription.updated':
      // Handle plan changes
      break;
  }
  
  res.json({ received: true });
});
```

## Key Events to Handle

| Event | Action |
|-------|--------|
| `invoice.paid` | Grant/extend access |
| `invoice.payment_failed` | Revoke access, email user |
| `customer.subscription.updated` | Handle plan changes |
| `customer.subscription.deleted` | Revoke all access |
| `charge.refunded` | Handle partial/full refunds |

## Best Practices

1. **Never expose secret key** - Use environment variables only
2. **Validate webhook signatures** - Always verify stripe-signature header
3. **Store customer IDs** - Link to your users for quick lookups
4. **Use idempotency keys** - For retry-safe API calls
5. **Set up retry logic** - Webhooks can fail; Stripe retries automatically
6. **Test with webhooks** - Use Stripe CLI: `stripe listen`

## For AI Co-Founder Stack

### V1 Integration (Basic)
- Manual invoice creation via dashboard
- Simple webhook for payment confirmation
- Customer portal link for self-service

### V2 Integration (Pro)
- Full API invoice automation
- Subscription management
- Usage-based billing support

### V3 Integration (Enterprise)
- Multi-currency support
- Connect for marketplace/partner splits
- Advanced fraud detection (Radar)

## Testing

- Use Stripe Test Mode (sk_test_xxx)
- Test card numbers: 4242424242424242
- Webhook CLI: `stripe listen --forward-to localhost:3000/webhook`

## Resources

- Docs: https://docs.stripe.com
- API Reference: https://docs.stripe.com/api
- Webhook Quickstart: https://docs.stripe.com/webhooks/quickstart

---

*Researched: February 20, 2026*
