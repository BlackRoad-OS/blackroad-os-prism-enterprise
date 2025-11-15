# Funding Intake Kit — 48-Hour Cash-In

**Owner:** Alexa Louise • BlackRoad  
**Purpose:** Turn “we might have funding” into money-in-bank fast, without selling the company.  
**Use:** Pick your lane below and follow the checklist. Copy/paste the templates.

---

## 0) Pick a Lane

* **A) Customer cash (fastest):** You have a buyer for consulting/POC.
* **B) Investor cash:** Someone wants to invest (angel/VC).
* **C) Grant cash:** A grant award/approval is pending.

> If you can do A **and** B, do A first (cash now), then close B cleanly.

---

## A) Customer Cash — 24–72 Hours

**Goal:** Send an invoice + contract and receive ACH/wire.

### Checklist

1. **Entity & EIN** (any of: existing LLC/C-Corp/sole prop).
2. **Bank account** (business if you have it; personal only as last resort).
3. **Payment rails**: Secure ACH payment link ready; only upload bank details inside the client's AP portal if they insist.
4. **Paperwork**: Short **MSA + SOW** or a one-page Service Order.
5. **Tax form**: US clients usually ask for **W-9** (or W-8 if non-US).

### One-Page Service Order (short form)

```
Service Order — BlackRoad
Client: ________________________  Date: ____________
Scope: Deploy Prism Console (registry, admissions, vitals) + training
Term: 4 weeks from start date; standard business hours
Deliverables:
  • Week 1: Agent inventory & risk assessment
  • Weeks 2–3: Deploy Prism + OpenTelemetry; dashboards live
  • Week 4: Policies + training; runbooks handed over
Fees: USD $50,000 fixed, 50% due at signing, 50% at Week 4
Payment: ACH via secure payment link within 5 business days of invoice
IP: Pre-existing IP remains owner’s; client receives usage rights to outputs
Confidentiality: Mutual; 2 years; carve-outs for public info/order of court
Limitation of Liability: Capped at fees paid; no consequential damages
Signatures: __________________ (Client)   __________________ (BlackRoad)
```

### Invoice Template (ACH preferred)

```
INVOICE  #BR-{YYYYMMDD-001}
Bill To: {Client Name}
Email: {ap@client.com}

Description: Prism Console POC (per Service Order)
Amount Due: $25,000 (50% upfront)
Due: Net 5

Payment: Pay via secure link — {PAYMENT_LINK}
If AP requires a direct bank upload, reply: "Reply with AP portal link for secure bank info upload."
Notes: W-9 (EIN only) available on request.
```

---

## B) Investor Cash — 7–14 Days (Clean Close)

**Default:** Use a **post-money SAFE**; incorporate if needed; wire to business bank.

### Steps

1. **Confirm basics (same-day)**
   • Amount $____  • Instrument: SAFE  • Valuation Cap: $____ (or Discount: __%)
   • Name/legal of investor + contact + KYC docs.
2. **Entity in place**
   • If none, form **Delaware C-Corp** (common investor preference).
   • File for **EIN**; set up **board consents** and **founder stock** soon after.
3. **Bank + Cap Table**
   • Open business bank; create a simple cap table (founders + SAFE).
   • Designate a corporate email and address for notices.
4. **Paperwork**
   • Fill the SAFE (company, investor, amount, date, cap or discount).
   • Optional: side letter for **pro rata** or **information rights** (if requested).
   • Send wiring instructions; countersign upon receipt.
5. **Receipts**
   • Email investor a PDF package: signed SAFE, wire receipt, bank confirmation.

### Cover Email (to investor)

```
Subject: BlackRoad — SAFE + Wiring Instructions

Hi {Name},
Attached is the post-money SAFE for ${AMOUNT} with a ${CAP} valuation cap.
Wiring instructions are below. We’ll countersign on receipt and send the
closing packet (SAFE + wire receipt) same day. Happy to answer anything.

— Alexa
```

### Wiring Block (copy into email)

```
BLACKROAD, INC.  — Incoming Wire
Bank: __________________________
Address: _______________________
Routing (ABA): _________________
Account Number: ________________
Beneficiary: BLACKROAD, INC.
Reference: SAFE — {Investor Name}
```

> **Note:** If you must accept funds before incorporation, ask counsel about
> holding in escrow or a sign-now/fund-on-incorporation workflow. Cleanest path is
> forming the entity first.

---

## C) Grant Cash — Timeline Varies

**Federal (SBIR/STTR, etc.)** often requires registrations that can take time.

### Steps

1. Confirm award/amount and the **payor’s requirements**.
2. Ensure your **entity, EIN, and bank** match the application.
3. Complete the required registrations/portals; submit banking info.
4. Sign the award agreement; diarize reporting and compliance dates.
5. Create a **grant ledger** (separate class code) and a deliverables calendar.

---

## Banking & Payments Quickstart

* Prefer **business banking**; keep funds separate from personal.
* Offer a secure **ACH payment link**; only share wire instructions inside a verified AP portal.
* Keep a **standard wiring block** handy for portal uploads; include invoice number in memo.
* Maintain a hosted **payment link** (Stripe, QuickBooks, PayPal) so no bank numbers travel by email.

---

## Data Room (lightweight)

* Deck (Receipts), 3-min demo video link
* One-page overview (problem → solution → proof → ask)
* Service Order or SAFE (unsigned), wiring block
* Basic financial model + pricing one-pager
* Contact sheet

---

## OpenTelemetry Proof Pack (attach to every deal)

* Dashboard panel: **refusals avoided**, **policy hits**, **trust score**, **CHSH value**
  * 1 linked **artifact JSON** from a CHSH run
  * 1 trace showing admissions → vitals → agent action
  * README snippet explaining data retention/redaction

---

## Pitfalls to Avoid

* Mixing personal/business funds; fix with a business account ASAP.
* Taking investor money without signed paperwork.
* Over-promising IP assignment; keep pre-existing IP with BlackRoad.
* Storing PII in logs; redact before export.

---

## Two-Email Sequence (Customer)

**Email 1 — Close**

```
Subject: Prism Console POC — Service Order + Invoice
Hi {Name}, attaching a one-page Service Order and the initial invoice ($25k).
ACH/wire preferred; once paid, we kick off on {DATE}. Let me know if AP needs
anything (W-9 attached).
— Alexa
```

**Email 2 — Kickoff**

```
Subject: Prism Console POC — Kickoff Call & Access
Great — booking a 45-min kickoff for {DATE}. Please add:
• point of contact, staging URL, security lead, and AP contact
We’ll bring the telemetry plan + runbook.
— Alexa
```

---

## Decision Tree (fast)

* **Is there a paying customer today?** → A.
* **Is an investor ready today?** → B.
* **Is a grant approved?** → C.
* **None yet?** → Send demos + deck; book discovery; keep pipeline moving.
