# Paddle Setup — The Mother's Code

The website is fully pre-wired for Paddle checkout. Once you complete the
steps below, paste two values into `website/app.js` and payments go live.
Until then, the Buy button falls back to an email-order link (so it never
dead-ends a customer).

---

## 1. Create your Paddle account

1. Sign up at https://www.paddle.com (choose **Paddle Billing**, not Classic).
2. You will get a **sandbox** account immediately (for testing) — the **live**
   account requires website verification (step 2).

## 2. Website verification (already prepared for you)

Paddle reviews your website before approving a live account. Submit
`https://www.the-mothers-code.com` — the checklist items they look for are
already in place:

- [x] Product clearly described with pricing ($14.99, PDF edition)
- [x] Terms & Conditions page (`/terms.html`)
- [x] Privacy Policy page (`/privacy.html`)
- [x] Refund Policy page (`/refunds.html` — 14-day money-back)
- [x] Contact email visible in the footer
- [x] Site live over HTTPS
- [x] Support email `contact@the-mothers-code.com` (live mailbox, shown in footer)

## 3. Create the product in Paddle

Dashboard → **Catalog → Products → New product**:

- Name: `The Mother's Code (ebook PDF)`
- Tax category: **eBooks / digital books** (important — gets correct VAT treatment)
- Add a **Price**: one-time, `USD 14.99`
- Copy the **Price ID** (starts with `pri_`)

## 4. Get your client-side token

Dashboard → **Developer tools → Authentication → Client-side tokens → New**.
Copy the token (`live_...` for production, `test_...` in sandbox).

## 5. Paste into the site

Open `website/app.js` — the config block is at the very top:

```js
var PADDLE_ENV = "sandbox";      // → "production" when going live
var PADDLE_CLIENT_TOKEN = "";    // ← paste token here
var PADDLE_PRICE_ID = "";        // ← paste pri_... here
```

Commit + push → Vercel redeploys → the Buy button opens Paddle's overlay
checkout, and successful payments land on `/thank-you.html` with the PDF
download.

## 6. Approve the domain for checkout

Dashboard → **Checkout → Website approval**: add
`the-mothers-code.com`. Paddle only opens checkout on approved domains
(approval covers www too). ✅ DONE — approved 13 July 2026.

## 7. Test before going live

In sandbox mode use Paddle's test card `4242 4242 4242 4242`, any future
expiry, any CVC. Confirm: overlay opens → payment succeeds → you land on the
thank-you page → the PDF downloads.

---

### Notes

- Paddle is a **merchant of record**: they handle VAT/sales tax, invoices,
  and refunds on your behalf — nothing extra to set up.
- The download page (`/thank-you.html`) is a simple unlisted URL. Good enough
  to start selling; if piracy ever becomes a real problem we can switch to
  expiring signed links later.
- Paddle fee (checkout, as of 2026): ~5% + $0.50 per transaction.
