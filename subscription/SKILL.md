# Subscription Test Suite

> This file is the skill document for the Subscription loyalty program test suite.
> Fill in each section step by step as we review the test scripts.

## Execution Notes

- Tests in this suite are run **code-free via MCP Playwright** — the user provides a plain-language prompt, and Claude navigates and interacts using browser snapshots and MCP tools. No Playwright test scripts are written or executed.
- **Session isolation (default):** At the start of every new scenario, always start clean — navigate to the table URL first, then clear all storage and cookies, then navigate again. Exact steps:
  1. `browser_navigate` to the table URL (so the page origin is set and storage/cookies are accessible)
  2. `browser_evaluate`: clear all storage AND cookies:
     ```js
     localStorage.clear();
     sessionStorage.clear();
     document.cookie.split(";").forEach(c => {
       document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date(0).toUTCString() + ";path=/");
     });
     ```
  3. `browser_navigate` to the table URL again (fresh load with clean state)
  This ensures auth cookies from previous scenarios do not bleed into the new one — clearing only localStorage/sessionStorage is NOT sufficient because the app stores auth tokens in cookies. Do this automatically before every scenario unless told otherwise.
- **Exception:** Only skip cleanup and reuse the existing session if the user explicitly says to continue with the same login or same tab.
- **Teardown:** After every scenario, close the browser with `browser_close` — unless the next scenario explicitly reuses the same session.
- MCP Playwright runs in **headless mode** by default. Native browser dialogs (e.g. "Save password?", "Save card?") do not appear in headless mode. If the user explicitly asks to run headed, the `--headless` flag can be removed from the MCP server config.
- After navigating to a new page or waiting for a response, always take a fresh snapshot before clicking — refs go stale after page state changes.
- If a dialog/modal is already visible in the current snapshot, click its elements directly — do NOT take another snapshot first. Taking an extra snapshot after an action that opens a dialog causes unnecessary delay.
- For elements inside nested iframes (e.g. 3D Secure dialog), always take a fresh snapshot after typing before clicking the submit button — iframe re-renders invalidate refs.
- **3D Secure redirect handling:** After clicking "Continue" in the 3DS dialog, **wait 6 seconds** (`browser_wait_for time=6`) to give the auto-redirect time to fire — do NOT take a snapshot immediately. After waiting, take a snapshot and check the page state:
  - If the confirmation page is visible ("Payment was successful") → done.
  - If a "Completing your payment" holding screen is showing with a "Click here if you're not redirected automatically" link → **click it**. Confirmed live (2026-08-08): this is the correct recovery and completes the redirect — earlier guidance here assumed clicking it broke session context via `window.top.location.replace(flow-redirect-url)`; that assumption was wrong. After clicking, wait for `"Payment was successful"` with up to 45 seconds.
  - If still stuck after clicking the link (no result after 45 seconds): mark the step as **BLOCKER FAILURE**, close the browser (`browser_close`), and report the scenario as FAILED. This is a known environment issue; the scenario must be re-run from scratch.

### Verification Strategy

**Never take a `browser_snapshot` purely to verify text or element presence.** Use Playwright's built-in wait mechanism instead:

| Check type | Tool | Notes |
|---|---|---|
| Text or element **visible** | `browser_wait_for text="..."` | Waits AND asserts — timeout = test failure |
| Page transition / navigation complete | `browser_wait_for text="<unique heading on target page>"` | |
| Toast / alert text | `browser_wait_for text="<toast text>"` | |
| Known computed value (e.g. amount after discount) | `browser_wait_for text="<expected value>"` | Only works when the value is inside the **same element** as any label text — if label and value are sibling elements, use two separate `browser_wait_for` calls |
| Element **NOT present** | `browser_evaluate: document.querySelector('...') === null` | Log pass/fail; do not use snapshot for absence |
| Checkbox checked state | `browser_evaluate: el.getAttribute('aria-checked') === 'true'` | |

**`browser_snapshot` is only allowed when:**
- You need a ref to **click or fill** a field — snapshot → get ref → interact.
- You need to **read a dynamic value** that cannot be predicted in advance (e.g. bill total before any discount action) — read it, calculate the expected result, then verify with `browser_wait_for text="<expected>"`.

### Failure Handling

**Non-blocker failures** (assertion mismatches — wrong amount, missing element, unexpected text):
- Log the failure with expected vs. actual values.
- Continue the scenario to the end.
- Include all failures in the final summary report.

**Blocker failures** (page stuck, payment not completing, 500 errors):
- Definition: any `browser_wait_for` that does not resolve, a pending page that does not transition, or a visible error ("500", "Something went wrong") that prevents the next step.
- **Retry once**: attempt the triggering action again (e.g. click "Check the status", reload if safe).
- **Timeout: 45 seconds** — if the blocker is not resolved within 45 seconds total (across both attempts), stop the scenario immediately, close the browser, and report as FAILED with the stuck step identified.

Blocker situations:
- `browser_wait_for "Payment was successful"` does not resolve within 45s
- Pending page does not auto-refresh to a result within 60s
- HTTP 500 or "Something went wrong" visible on page
- 3DS dialog still showing 60s after clicking "Continue" with no auto-redirect

---

## Pages & Elements

### Common Elements

| Element | Pages Present | Locator Strategy | Notes |
|---|---|---|---|
| Login Button | Landing, Billing, Confirmation | `button` with text `"Login"` | Top-right area — replaced by profile icon after login |
| Burger Menu Button | Landing, Billing, Confirmation | `button` (icon only, no text) — last button in top-right area | Always present regardless of login state |
| Language Selector | Landing, Billing only | `button` with text `"EN"` (or current lang code) | Not present on Confirmation Page |

**Burger Menu (when logged in) contains:**
| Menu Item | Locator Strategy |
|---|---|
| Log out | `button` with text `"Log out"` — triggers Logout Confirmation Dialog |
| Manage subscription | `button` with text `"Manage subscription"` |
| Account details | `button` with text `"Account details"` |
| Switch account | `button` with text `"Switch account"` |

**Logout Confirmation Dialog** — appears after clicking "Log out" in the burger menu:
| Element | Locator Strategy | Notes |
|---|---|---|
| Confirm Log Out Button | `button` with text `"Log out"` inside the confirmation dialog | Actually performs the logout |
| Stay With Qlub Button | `button` with text `"Stay with Qlub"` | Cancels logout, dismisses dialog |

---

### Landing Page

The first page the user sees after scanning the QR code.

| Element | Locator Strategy | Notes |
|---|---|---|
| Pay Now Button | `button` with text matching `"Pay now"` | Shows bill amount (e.g. "Pay now 37.00") |
| Landing Page Bill Amount | numeric text node inside the Pay Now button | Parse number after `"Pay now "`, e.g. `"Pay now 37.00"` → `37.00` |
| View Menu Button | `button` with text `"View menu"` | Links to legacy menu |
| Weekly Eligible Limit Banner | rounded card with qlub icon, `heading`/`paragraph` text `"Weekly eligible limit reached"` + `"You've used all eligible discounts for this week"` | Shown on the Landing Page (above the item list) when a subscriber's discount cap for the period has been reached — e.g. Cap Limit scenario after 3 discounts used |

---

### Billing Page

The second page — shows itemized bill, subscription widget, tip section, and payment form.

| Element | Locator Strategy | Notes |
|---|---|---|
| Payable Amount | `generic` with text `"Payable amount"` → sibling numeric text node | e.g. `130.00` — this is the amount after any discounts |
| Subscription Checkbox | `checkbox` containing a `button` — located above the payable amount section | Label text starts with `"Subscribe now to save"` followed by discount amount and `"on this bill"` |
| Login Now Button | `button` with text `"Login now"` | Below the subscription checkbox, inside the "Already a qlub+ member?" section |
| Split Bill Button | `button` with text `"Split bill"` | Bottom action area |
| Pay Fully Button | `button` with text `"Pay fully"` | Bottom action area |
| qlub+ Discount Amount | numeric text node inside the `"qlub plus discount"` row | Visible only after subscription is applied — e.g. `-30.00`; verify this matches the expected discount |
| You Pay Amount | numeric text node next to `"You pay"` label | Final amount user pays after discount — e.g. `9.00`; different from Payable Amount when discount is applied |
| Pay Full Bill Button | `button` with text `"Pay full bill"` | Replaces Split/Pay Fully buttons after subscription discount is applied |
| Card Number Field | `textbox` with placeholder `"1234 1234 1234 1234"` inside iframe | Use test Visa card below |
| Expiry Month Field | `textbox` with placeholder `"12"` inside iframe | |
| Expiry Year Field | `textbox` with placeholder `"27"` inside iframe | |
| CVV Field | `textbox` with placeholder `"123"` inside iframe | |
| Pay Button | `button` with text `"Pay"` | Final payment trigger |
| Edit Split Button | `button` with text `"Edit split"` | Visible after split is confirmed — replaces Split Bill / Pay Fully buttons |
| View Bill Button | `button` with text `"View bill"` | Visible after split is confirmed — shows full itemized bill |
| Your Share Amount | numeric text node next to `"Your Share"` label | Visible after split confirmed — e.g. `28.50` |
| You Are Paying For Your Share Text | `paragraph` with text `"You are paying for your share"` | Replaces "Inclusive of taxes and charges" after split |
| Tip Not Now Button | `button` with text `"Not now"` | Skips tip; no tip amount is added |
| Tip 5.00 Button | `button` with text `"5.00"` (or containing `"5"`) in the tip section | Adds 5.00 AED tip |
| Tip 10.00 Button | `button` with text `"10.00"` (or containing `"10"`) in the tip section | Adds 10.00 AED tip — **default tip** unless the scenario specifies otherwise |
| Tip 15.00 Button | `button` with text `"15.00"` (or containing `"15"`) in the tip section | Adds 15.00 AED tip |

**Test Card (Visa):**
- Card Number: `4242 4242 4242 4242`
- Expiry: `12/30`
- CVV: `444`

---

### Split Bill Dialog

Opens as a bottom sheet when the user clicks "Split bill" on the Billing Page. Contains three split options.

**Step 1 — Split option selection sheet:**

| Element | Locator Strategy | Notes |
|---|---|---|
| Dialog Title | `heading` with text `"Split the bill"` | Top of the bottom sheet |
| Pay For Your Items Option | `heading` with text `"Pay for your items"` + adjacent `button` with text `"select"` | Split by item |
| Divide Equally Option | `heading` with text `"Divide the bill equally"` + adjacent `button` with text `"select"` | Equal share split — use this for Scenario 4+ |
| Pay Custom Amount Option | `heading` with text `"Pay a custom amount"` + adjacent `button` with text `"select"` | Custom amount split |
| Close Button | `button` (icon only) inside the dialog header | Dismisses the bottom sheet |

**Step 2 — Divide equally confirmation sheet** (appears after selecting "Divide the bill equally"):

| Element | Locator Strategy | Notes |
|---|---|---|
| Sheet Title | `heading` with text `"Divide the bill equally"` | Top of confirmation sheet |
| Total Bill Amount | numeric text node next to total bill display | e.g. `57.00` |
| Total People Counter | `generic` with text matching the total count (e.g. `"2"`) | Number of people at the table |
| You Pay For Counter | `generic` with text matching your count (e.g. `"1"`) | How many shares you're paying |
| Increment/Decrement Buttons | `button` with `img` icon — two pairs, one for each counter | Adjust total people and your share count |
| Your Share Amount | numeric text node next to `"Your share"` label | Calculated share — e.g. `28.50` |
| Remove Split Button | `button` with text `"Remove split"` | Cancels the split selection |
| Confirm Button | `button` with text `"Confirm"` | Applies the split and returns to billing page |

---

### Subscription Dialog

Opened when the user clicks the Subscription Checkbox on the Billing Page. Appears as a dialog/modal overlay.

| Element | Locator Strategy | Notes |
|---|---|---|
| Monthly Price | numeric text node inside `"Only X monthly"` paragraph | e.g. `20` — the subscription fee |
| Average Savings | numeric text node inside `"Save X on Average"` paragraph | e.g. `150` |
| Discount Percentage Text | `paragraph` with text `"Save up to 30% per bill"` | Verify exact percentage |
| Restaurant Count Text | `paragraph` with text containing `"+600 restaurants"` | Verify exact number |
| Country Text | `paragraph` with text `"across the UAE"` | Static label |
| Subscribe Button | `button` with text matching `"Subscribe & Save"` | Contains the welcome discount amount (e.g. `30`) |
| Subscribe Button Price | numeric text node inside the Subscribe Button | Reflects the welcome discount amount (e.g. `30`), not the monthly fee (`20`) |
| Close Button | `button` (icon only) inside the dialog header | Dismisses the dialog |

---

### Phone Number Dialog

Appears after clicking "Subscribe & Save" on the Subscription Dialog. Used for both new and existing user login.

| Element | Locator Strategy | Notes |
|---|---|---|
| Mobile Number Input | `textbox` with placeholder `"Mobile number"` | Pre-filled with country code `+971` |
| Receive Code Button | `button` with text `"Receive Code"` | Disabled until a valid number is entered |

**Generating a random UAE number for new users:**
- Format: `+971 5X XXXXXXX` (9 digits after country code, starting with `5`)
- Example: `+971501234567`
- No OTP verification in test environment — any valid format works

**⚠️ OTP Rate Limit:** Each phone number is blocked after **4 OTP requests within 1 hour**.

**Rotation rule:** Use each number for up to 4 OTP-requiring scenarios, then switch to the next one in the list.

**General subscribers** (subscription_type = "General"):
1. `+971507391824`
2. `+971523456789`
3. `+971589012347`

When all numbers are rate-limited, generate a new UAE number, complete the sign-up flow, and add it to this list.

**Standalone subscribers** (subscription_type = "Standalone"):
_(empty — add new numbers here)_

---

### OTP Dialog

Appears after clicking "Receive Code" on the Phone Number Dialog. Used to verify the user's mobile number.

| Element | Locator Strategy | Notes |
|---|---|---|
| Displayed Phone Number | `paragraph` containing the phone number (e.g. `"+971507391824"`) | Verify this matches the entered number |
| Edit Phone Button | `button` (icon only) next to the displayed phone number | Allows changing the number |
| Sent To Text | `paragraph` with text matching `"The 5-digit code has been sent to"` | Contains the phone number — verify number inside |
| OTP Input 1–5 | `textbox` with name `"Please enter OTP character 1"` through `"...character 5"` | 5 separate inputs; enter each digit individually |
| SMS Button | `button` with text `"SMS"` | Resend via SMS — disabled during countdown |
| WhatsApp Button | `button` with text `"WhatsApp"` | Resend via WhatsApp — disabled during countdown |
| Subscribe Button | `button` with text `"Subscribe"` | Disabled until valid OTP is entered |

**Valid OTP for test environment:** Always use `12345` — works for any phone number in staging.

---

### 3D Secure Dialog

Appears after clicking Pay when the card requires 3D Secure authentication. Shown as a dialog overlay ("3D Secure 2 Authentication"). Located inside nested iframes.

| Element | Locator Strategy | Notes |
|---|---|---|
| Password Input | `textbox` with hint/placeholder `"Hint: Checkout1!"` inside nested iframes | Enter valid or invalid password to test both flows |
| Continue Button | `button` with text `"Continue"` inside the 3DS iframe | Submits the authentication |

**Valid password:** `Checkout1!` — use this for successful payment scenarios.
**Invalid password:** enter anything else to test failed 3DS scenarios.

**Post-3DS fallback button:** ⚠️ Do NOT click any "Click here to continue" or similar fallback/redirect links that appear after clicking "Continue". These links call `window.top.location.replace(flow-redirect-url)` which breaks the app's session context. Instead, use `browser_wait_for` for the expected result page (e.g. "Payment was successful" or "Welcome to qlub+") with up to 45 seconds — the postMessage redirect fires automatically.

---

### Confirmation Page

The third page shown after a successful payment. No Language Selector here.

| Element | Locator Strategy | Notes |
|---|---|---|
| Payment Success Text | `paragraph` with text `"Payment was successful"` | Confirms payment went through |
| Fully Paid Label | `paragraph` with text `"Fully paid"` | Shown when the entire bill is paid |
| You Paid Amount | numeric text node in the paragraph AFTER `"You paid"` | e.g. `182.00` — ⚠️ `"You paid"` and the amount are in **sibling paragraphs**, not one element; verify with TWO separate `browser_wait_for` calls: `browser_wait_for text="You paid"` then `browser_wait_for text="182.00"` — a combined `text="You paid 182.00"` will always fail |
| Back to Home Button | `button` with text `"Back to home"` | Navigates back to Landing Page |
| Saved Amount | numeric text node inside `"You've saved X on this bill"` paragraph | e.g. `30.00` — verify this matches the expected discount amount |
| Congratulations Popup (Billing) | `alert` role element — appears briefly on the billing page immediately after subscribing | Text: `"Your qlub account is created!"` — dismisses quickly; assert right after Subscribe button click |
| Congratulations Dialog (Confirmation) | `dialog` role element on confirmation page after first subscription | Contains `"Congratulations!"` heading + `"You've saved X on this bill"` + `"venues"` button |

---

### Payment Unsuccessful Page

Shown after a failed regular bill payment (e.g. wrong 3DS password). Not the same as the "Card Verification Failed" screen (Standalone-only).

| Element | Locator Strategy | Notes |
|---|---|---|
| Error Icon | red diamond icon with X — decorative image | Visual indicator only |
| Heading | `paragraph` with text `"Payment was unsuccessful!"` | Main failure message |
| Subtitle | `paragraph` with text `"Please try again"` (displayed in red) | Below heading |
| Table Name Text | `paragraph` or `generic` with the table display name (e.g. `"Table 10 (Table 10)"`) | Inside the transaction summary card |
| Failed Badge | `generic` or `paragraph` with text `"Failed"` | Red badge inside the card |
| Timestamp | `paragraph` with date/time of the failed attempt | e.g. `"12:30 AM, May 6, 2026"` |
| Try Again Button | `button` with text `"Try Again"` | Returns user to Billing Page with discount still applied |
| Back to Home Button | `button` with text `"Back to home"` | Returns user to Landing Page |

---

### Manage Subscription Page

Accessible via Burger Menu → "Manage subscription". Shows subscription status and benefits.

| Element | Locator Strategy | Notes |
|---|---|---|
| Total Saved Amount | numeric text node inside `"You've saved a total of X"` paragraph | e.g. `30.00` — cumulative savings since subscription start |
| Member Since Text | `paragraph` with text matching `"since"` + date | e.g. `"since 30th Apr 2026"` |
| Renewal Date Text | `paragraph` with text matching `"Your subscription renews on"` | e.g. `"1st Jun 2026"` |
| Next Billing Amount | numeric text node inside `"Next billing amount is X"` | e.g. `20.00` — monthly fee |
| Benefit 1 Title | `paragraph` with text `"Discounts and Complementary items"` | Under "Subscription benefits" section |
| Benefit 1 Description | `paragraph` with text starting `"Save instantly on your bill"` | |
| Benefit 2 Title | `paragraph` with text `"Effortless Savings"` | |
| Benefit 2 Description | `paragraph` with text starting `"Your rewards are automatically applied"` | |
| Cancel Subscription Button | `button` with text `"Cancel subscription"` | ⚠️ Do NOT click unless the test explicitly requires cancellation |

**Cancellation Flow** — appears after clicking "Cancel subscription":

| Element | Locator Strategy | Notes |
|---|---|---|
| Cancellation Reason Checkbox | `checkbox` elements inside the cancellation reason list | One or more checkboxes; select at least one before Confirm is enabled |
| Confirm Cancellation Button | `button` with text `"Confirm cancellation"` | Enabled only after at least one reason checkbox is checked |
| Keep Subscription Button (sheet) | `button` with text `"No, keep my subscription"` | Inside the confirmation bottom sheet — cancels the flow |
| Confirm Cancel Button (sheet) | `button` with text `"Yes, cancel my subscription"` | Inside the confirmation bottom sheet — finalises cancellation |
| Cancellation Success Toast | `alert` or toast element with text containing `"cancelled"` or `"unsubscribed"` | Appears briefly after confirming cancellation |

---

### Standalone Landing Page

The Landing Page shown when scanning a Standalone QR code. Identical layout to the standard Landing Page but includes a subscription banner prompting the user to subscribe.

| Element | Locator Strategy | Notes |
|---|---|---|
| Standalone Subscription Banner | `DIV[role="button"]` with class `styles-module-scss-module__iz-GHG__root` — **not visible in accessibility tree**; click via `browser_evaluate`: `document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root').click()` | Visible before subscription is active; image-based render, text is not in DOM |
| Subscribe CTA Button (banner) | Text: `"Unlock 2 Months Free"` — rendered as part of the banner image, **not a standard button**; click the banner div directly (see above) | Clicking navigates to `/subscription/introduction` |
| Pay now Button | `button` with text matching `"Pay now"` | Same as standard Landing Page; visible after subscription is active |
| Discount Banner (post-subscription) | paragraph with text `"You save X on this bill"` + `"Pay the bill to apply the discount"` | Replaces the subscription banner after the user has an active subscription |

---

### Standalone Subscription Page

A full-screen (or overlay) page that opens when the user clicks the Subscribe CTA on the Standalone Landing Page banner. Describes the qlub+ subscription offer and contains a Subscribe button.

| Element | Locator Strategy | Notes |
|---|---|---|
| Subscribe Button | `button` with text `"Subscribe"` or `"Subscribe & Save"` | Opens Phone Number Dialog if user is not logged in; opens 1 AED payment screen directly if user is already logged in |
| Close Button | `button` (icon only, X shape) in the top corner of the page/overlay | Dismisses the Subscription Page and returns to the Landing Page |

---

### Standalone Subscription Payment Screen

Appears as a bottom sheet after OTP verification in the Standalone flow. Contains a 1 AED card charge to activate the subscription.

| Element | Locator Strategy | Notes |
|---|---|---|
| Phone Shown | `paragraph` containing the user's phone number (e.g. `"+97197150888"`) | Confirm it matches the number entered |
| Charge Notice Text | `paragraph` with text `"A ₿ 1 charge will be made and refunded to verify your card."` | Verify this text is present |
| Card Number Field | `textbox` with placeholder `"1234 1234 1234 1234"` (Checkout.com iframe) | Use test Visa card `4242 4242 4242 4242` |
| Expiry Date Field | `textbox` with placeholder `"MM/YY"` (Checkout.com iframe) | Single combined field — enter `1230` |
| Security Code Field | `textbox` with placeholder `"CVV"` (Checkout.com iframe) | Enter `444` |
| Subscribe Now Button | `button` with text `"Subscribe Now"` | Submits the 1 AED card charge |

---

### Welcome to qlub+ Screen

Full-screen confirmation shown after the 1 AED Standalone subscription payment succeeds.

| Element | Locator Strategy | Notes |
|---|---|---|
| Welcome Heading | `heading` or prominent text `"Welcome to qlub+"` | Verify exact text |
| Free Trial Text | `paragraph` with text `"Your 7 days free trial is active now!"` | Verify exact text |
| Pay the Bill Button | `button` with text `"Pay the Bill"` | Navigates back to the Standalone Landing Page with discount applied |

---

### Card Verification Failed Screen

Full-screen error page shown after the 1 AED Standalone subscription payment fails (e.g. 3DS wrong password). Subscription is NOT activated.

| Element | Locator Strategy | Notes |
|---|---|---|
| Error Icon | red diamond icon with X — decorative image | Visual indicator only |
| Heading | `heading` or prominent text `"Card Verification Failed!"` | Verify exact text |
| Description Text | `paragraph` with text `"We couldn't verify your card details, so your subscription wasn't activated. Please try again."` | Verify exact text |
| Try Again Button | `button` with text `"Try again"` | Navigates back to the 1 AED payment screen to retry |

---

## Domain Rules

### Subscription Types

#### General Subscription
The standard qlub+ subscription. Users subscribe via the Subscription Checkbox or "Login now" button on the Billing Page, or via the top Login button (Club login) on any page. Discount is percentage-based (5% of bill amount) applied automatically on every payment. Stored in DB as `"subscription_type": "General"`.

#### Standalone Subscription
A separate subscription product accessed via dedicated Standalone QR codes (`furkanStandaloneAutomation`). The flow differs from General:
1. User scans a Standalone QR and lands on the Landing Page, where a subscription banner is immediately visible.
2. If not logged in, the user logs in (Club login via top Login button or inline login flow).
3. After login, a dedicated payment screen appears — the user enters card details and pays **1 AED** to activate the Standalone subscription.
4. Once the 1 AED payment is confirmed, the user is taken to the Billing Page where the qlub+ discount is already applied.
5. Stored in DB as `"subscription_type": "Standalone"`.

### DB Verification — subscription_type
Every scenario that creates or uses a subscription should verify the `subscription_type` field in the `cust_customer_mapping` table (via `get_customer_mapping_by_phone`) as part of its DB verification step:
- General subscription flows → expect `"subscription_type": "General"`
- Standalone subscription flows → expect `"subscription_type": "Standalone"`

This check is always a **non-blocker** — log expected vs. actual if it fails but continue the scenario.

---

## DB Helpers

> DB queries are executed via `NODE_PATH=$(npm root -g) node -e "..."`. Connection details are taken from the `db-customer` MCP server config in `~/.claude/settings.json`: host `127.0.0.1`, port `5433`, database `db-customer`.

### get_customer_mapping_by_phone(phone)

Returns all `cust_customer_mapping` rows for the user with the given phone number. `phone` must be in international format starting with `+` (e.g. `+971507391824`).

```js
// Only <PHONE> changes — replace with the target number
NODE_PATH=$(npm root -g) node -e "
process.env.NODE_PATH = '$(npm root -g)';
require('module').Module._initPaths();
const {Client} = require('pg');
const client = new Client({ host:'127.0.0.1', port:5433, user:'furkan.kurt@qlub.io', password:'49E#PpLb3kEzn]', database:'db-customer', ssl:false });
async function run() {
  await client.connect();
  const res = await client.query(\`
    SELECT * FROM \"public\".\"cust_customer_mapping\"
    WHERE cust_id IN (
      SELECT cust_id FROM \"public\".\"cust_customer_mapping\"
      WHERE extra_info ->> 'phone' = '<PHONE>'
    )
    ORDER BY id DESC LIMIT 50
  \`);
  console.log(JSON.stringify(res.rows, null, 2));
  await client.end();
}
run().catch(e => console.error('ERROR:', e.message));
"
```

---

## Config Defaults

### Scenario Table Assignments

Each scenario uses a dedicated table to avoid session/state collisions between runs.

| Scenario | Table(s) |
|---|---|
| Scenario 1 — New User: Welcome Discount + General Discount + Cancel Subscription | Table 1 (welcome discount), Table 2 (general discount) |
| Scenario 2 — New User: 3DS Failure → Try Again → Successful Payment | Table 10 |
| Scenario 3 — Existing User via Subscription Checkbox | Table 3 |
| Scenario 4 — Existing User via Login Button | Table 4 |
| Scenario 5 | Table 5 |
| Scenario 6 | Table 6 |
| Scenario 7 — Tip is Not Included in Discount (after login) | Table 7 |
| Scenario 8 — Tip is Not Included in Discount (before login) | Table 8 |
| Scenario 9 — Subscription with Qlub Login | Table 9 |
| Scenario 10 — New Standalone Subscriber + Cancel Subscription | SS Table 1 (staging) / Table 11 (dev7) |
| Scenario 11 — Standalone Banner/Subscription Page Resilience + New User Subscribe | SS Table 2 (staging) / Table 12 (dev7) |
| Scenario 12 — Standalone 3DS Failure: Wrong Password × 3 → Card Verification Failed | SS Table 3 (staging) / Table 13 (dev7) |
| Scenario 13 — Cap Limit: General Discount Usage Cap (3 per Week) | CL Table 1, 2, 3 (discounted payments), CL Table 4 (cap reached, dev6) — CL Table 5 spare |

---

## Environment Variables

### Subscription Table URLs (Staging)

| Table | URL |
|---|---|
| Table 1 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/1/_/_/35f7042757` |
| Table 2 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/2/_/_/577429c297` |
| Table 3 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/3/_/_/fe5ae86801` |
| Table 4 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/4/_/_/89b432ecf2` |
| Table 5 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/5/_/_/4d4f041013` |
| Table 6 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/6/_/_/1097dc35ab` |
| Table 7 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/7/_/_/e402fc4578` |
| Table 8 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/8/_/_/8a6e85627b` |
| Table 9 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/9/_/_/5ebc39fdf1` |
| Table 10 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/10/_/_/1614099736` |
| Table 11 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/6d55f45b13` |
| Table 12 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/0562f7d18c` |
| Table 13 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/1741580c50` |
| Table 14 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/263474f54d` |
| Table 15 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/b39b2bfff2` |

### Standalone Subscription QR Table URLs (Staging)

> Uses `furkanSubscriptionAutomation` tables 11–13 (Standalone enabled on this restaurant). `furkanStandaloneAutomation` is no longer used.

| Standalone Table | Table # | URL |
|---|---|---|
| SS Table 1 (Scenario 10) | Table 11 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/6d55f45b13` |
| SS Table 2 (Scenario 11) | Table 12 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/0562f7d18c` |
| SS Table 3 (Scenario 12) | Table 13 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/1741580c50` |
| Spare | Table 14 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/263474f54d` |
| Spare | Table 15 | `https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/b39b2bfff2` |

### Subscription Table URLs (Dev7)

| Table | URL |
|---|---|
| Table 1 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/1/_/_/b3a8ca38ac` |
| Table 2 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/2/_/_/1c801f1d92` |
| Table 3 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/3/_/_/535bf09dc8` |
| Table 4 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/4/_/_/d7150ce236` |
| Table 5 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/5/_/_/a2eea2ada7` |
| Table 6 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/6/_/_/fdefd87d1d` |
| Table 7 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/7/_/_/4be020f7c0` |
| Table 8 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/8/_/_/9a21635749` |
| Table 9 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/9/_/_/0f4f965474` |
| Table 10 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/10/_/_/3cffd9ae87` |
| Table 11 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/20ab34b4f4` |
| Table 12 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/cd193aaa07` |
| Table 13 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/b92d1db193` |
| Table 14 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/cf2ae70d59` |
| Table 15 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/44dca92de9` |

### Standalone Subscription QR Table URLs (Dev7)

> Uses `furkanSubscriptionAutomation` tables 11–13 (Standalone enabled on this restaurant for dev7). `furkanStandaloneAutomation` does not exist on dev7 yet.

| Standalone Table | Table # | URL |
|---|---|---|
| SS Table 1 (Scenario 10) | Table 11 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/20ab34b4f4` |
| SS Table 2 (Scenario 11) | Table 12 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/cd193aaa07` |
| SS Table 3 (Scenario 12) | Table 13 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/b92d1db193` |
| Spare | Table 14 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/cf2ae70d59` |
| Spare | Table 15 | `https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/44dca92de9` |

### Subscription Table URLs (Dev6)

| Table | URL |
|---|---|
| Table 1 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/1/_/_/6bcd0e0209` |
| Table 2 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/2/_/_/28b4eeb023` |
| Table 3 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/3/_/_/e5e81e303f` |
| Table 4 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/4/_/_/5e0fc408f7` |
| Table 5 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/5/_/_/3677e863b4` |
| Table 6 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/6/_/_/cd4247d510` |
| Table 7 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/7/_/_/2afd455727` |
| Table 8 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/8/_/_/ec192e69e0` |
| Table 9 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/9/_/_/6e13ba8128` |
| Table 10 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/10/_/_/f09aaadc1d` |
| Table 11 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/b9ced8f2ba` |
| Table 12 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/bd00290186` |
| Table 13 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/0225dc6bd5` |
| Table 14 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/27477bb621` |
| Table 15 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/2d70377d66` |

### Standalone Subscription QR Table URLs (Dev6)

> Uses `furkanSubscriptionAutomation` tables 11–13 (Standalone enabled on this restaurant for dev6).

| Standalone Table | Table # | URL |
|---|---|---|
| SS Table 1 (Scenario 10) | Table 11 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/b9ced8f2ba` |
| SS Table 2 (Scenario 11) | Table 12 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/bd00290186` |
| SS Table 3 (Scenario 12) | Table 13 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/0225dc6bd5` |
| Spare | Table 14 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/14/_/_/27477bb621` |
| Spare | Table 15 | `https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/15/_/_/2d70377d66` |

---

### Cap Limit QR Table URLs (Dev6)

> Restaurant slug `subscriptionAutomationCapLimit` — dedicated to cap limit scenarios (to be defined). Other environments to be added when shared.

| Cap Limit Table | Table # | URL |
|---|---|---|
| CL Table 1 | Table 1 | `https://app-dev6.qlub.cloud/qr/ae/subscriptionAutomationCapLimit/1/_/_/c3aabd5650` |
| CL Table 2 | Table 2 | `https://app-dev6.qlub.cloud/qr/ae/subscriptionAutomationCapLimit/2/_/_/36dc40ce65` |
| CL Table 3 | Table 3 | `https://app-dev6.qlub.cloud/qr/ae/subscriptionAutomationCapLimit/3/_/_/73fd905fc9` |
| CL Table 4 | Table 4 | `https://app-dev6.qlub.cloud/qr/ae/subscriptionAutomationCapLimit/4/_/_/f89202f5e2` |
| CL Table 5 | Table 5 | `https://app-dev6.qlub.cloud/qr/ae/subscriptionAutomationCapLimit/5/_/_/6f465908ef` |

---

## Flows

### Scenario 1 — New User: Welcome Discount + General Discount + Cancel Subscription

**Goal:** A brand-new user subscribes to qlub+ on Table 1 and pays using the **welcome discount** (fixed 30 AED off, configured in the restaurant config). Then, without closing the browser, opens a second tab and pays Table 2 using the **general discount** (5% of the bill amount, applied automatically to all active subscribers). Browser is closed at the end.

**Discount terminology:**
- **Welcome discount** — fixed amount (30 AED) applied on the first payment when a new user subscribes. Configured per restaurant.
- **General discount** — percentage-based (5% of bill amount) applied on every subsequent payment for active subscribers. Always calculated dynamically from the actual bill amount.

**Tables used:** Table 1 (new user subscription + welcome discount) → Table 2 (returning subscriber + general discount)

---

#### Part 1 — Table 1: New User Subscription + Payment

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 1 URL.

**Step 1 — Navigate to Billing Page**

Click "Pay now" on the Landing Page.

**Step 2 — Read Payable Amount**

Read and store the **Payable Amount** (e.g. `251.00`) — it will be compared after the discount is applied.

**Step 3 — Open Subscription Dialog**

Click the Subscription Checkbox. Use `browser_wait_for text="Only 20 monthly"` to confirm the dialog is open — no snapshot needed. Then use `browser_wait_for` for each remaining item:
- `browser_wait_for text="Only 20 monthly"`
- `browser_wait_for text="Save 150 on Average"`
- `browser_wait_for text="Save up to 30% per bill"`
- `browser_wait_for text="+600 restaurants"`
- `browser_wait_for text="across the UAE"`
- `browser_wait_for text="Subscription auto-renews monthly, starting June 5th"` — date is always tomorrow's day-of-month, one month ahead (today = May 4 → tomorrow = May 5 → renewal = June 5th)
- `browser_wait_for text="30"` inside the Subscribe button

Take a snapshot **only** to get the ref for clicking `"Subscribe & Save"`.

**Step 4 — Subscribe with a new UAE number**

Click "Subscribe & Save". On the Phone Number Dialog:
- Generate a random valid UAE number: format `5XXXXXXXX` (9 digits starting with 5), e.g. `523456789`
- Type the 9-digit suffix into the input (country code is already there)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971523456789"` (replace with the actual generated number) — confirms the correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe".

**Step 5 — Post-subscribe Billing Page checks**

After clicking Subscribe, use `browser_wait_for` for each check — no snapshot needed for text assertions:
- `browser_wait_for text="Your qlub account is created!"` — waits and verifies the alert appeared
- `browser_wait_for text="The card used for this payment will be charged 20.00 per month for qlub+"`
- `browser_wait_for text="-30.00"` — verifies qlub plus discount row
- `browser_wait_for text="Pay full bill"` — verifies discount applied and button is visible
- `browser_wait_for text="<original − 30>"` — verifies Payable Amount decreased (e.g. if original was `251.00`, use `browser_wait_for text="221.00"`)
- To check Subscription Checkbox `[checked]` state: `browser_evaluate: document.querySelector('[role="checkbox"]').getAttribute('aria-checked') === 'true'`

**Step 6 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes, then wait for `"Payment was successful"`.

**Step 7 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="221.00"` (replace with calculated value: original − 30) — verifies the amount
- `browser_wait_for text="You've saved 30.00 on this bill"`
- `browser_wait_for text="Congratulations!"`

**Step 7a — DB Verification**

Call `get_customer_mapping_by_phone` (see DB Helpers) using the phone number generated in Step 4 (e.g. `+971523456789`).

From the returned rows, find the row where `module_cat = "subscription"` and verify its `extra_info`:
- `"status": "active"`
- `"subscription_type": "General"`

Log expected vs. actual if either assertion fails (non-blocker).

---

#### Part 2 — Table 2: Returning Subscriber Discount + Payment

**Setup:** Open a **new tab** (do not close the browser). Navigate to Table 2 URL in the new tab.

**Step 8 — Read bill amount and calculate expected discount**

After the page loads, read the bill amount from the Landing Page "Pay now" button text (e.g. `"Pay now 34.00"` → `34.00`). Calculate expected discount: `billAmount × 0.05`, rounded to 2 decimal places (e.g. `34.00 × 0.05 = 1.70`).

Use `browser_wait_for` to verify Landing Page banner:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5% value)
- `browser_wait_for text="Pay the bill to apply the discount"`

**Step 9 — Navigate to Billing Page**

Click "Pay now".

**Step 10 — Billing Page checks**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` (replace X with calculated 5%, e.g. `-1.70`) — verifies qlub plus discount row

**Step 11 — Pay**

Enter card details (same test Visa card). Click "Pay". Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 12 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with bill amount minus discount) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

---

#### Part 3 — Cancel Subscription

**Step 13 — Navigate to Manage Subscription**

Click the Burger Menu button (icon-only button, top-right corner of the confirmation page). The burger menu opens.

Click `"Manage subscription"`. The Manage Subscription page loads.

**Step 14 — Cancel subscription**

Click the `"Cancel subscription"` button.

The cancellation reason screen appears. `browser_wait_for text="Confirm cancellation"` — confirms the screen loaded. Take a snapshot to get the first checkbox ref, then check it.

`browser_wait_for text="Confirm cancellation"` — button should now be enabled. Take a snapshot to get its ref, then click it.

**Step 15 — Confirm cancellation bottom sheet**

Use `browser_wait_for` to confirm both buttons are visible before clicking:
- `browser_wait_for text="No, keep my subscription"`
- `browser_wait_for text="Yes, cancel my subscription"`

Take a snapshot to get the ref, then click `"Yes, cancel my subscription"`.

**Step 16 — Verify cancellation success**

`browser_wait_for text="cancelled"` — verifies the success toast; if `"cancelled"` not found, try `browser_wait_for text="unsubscribed"`. No snapshot needed.

**Step 17 — DB Verification**

Call `get_customer_mapping_by_phone` (see DB Helpers) using the same phone number generated in Step 4.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "suspended"`

Log expected vs. actual if the assertion fails (non-blocker).

---

### Scenario 2 — New User: 3DS Failure → Try Again → Successful Payment

**Goal:** A brand-new user subscribes to qlub+ via the Subscription Checkbox and receives the welcome discount (30 AED). During payment, the user enters an incorrect 3DS password — the payment fails and the "Payment was unsuccessful!" page is shown. The user clicks "Try Again", returns to the Billing Page where the subscription checkbox remains checked and the 30 AED discount is still applied. The user then re-enters card details, submits the correct 3DS password, and completes the payment successfully. Confirmation page and DB are verified.

**Tables used:** Table 10

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 10 URL.

**Step 1 — Navigate to Billing Page**

Click "Pay now" on the Landing Page.

**Step 2 — Read Payable Amount**

On the Billing Page, read and store the **Payable Amount** shown in the `"Payable amount"` section (e.g. `180.00`). This will be compared after the welcome discount is applied.

**Step 3 — Open Subscription Dialog**

Click the Subscription Checkbox. Use `browser_wait_for` to verify dialog content — no snapshot needed for text assertions:
- `browser_wait_for text="Only 20 monthly"`
- `browser_wait_for text="Save up to 30% per bill"`
- `browser_wait_for text="30"` — verifies Subscribe button price

Take a snapshot only to get the ref for clicking `"Subscribe & Save"`.

**Step 4 — Subscribe with a new UAE number**

Click "Subscribe & Save". On the Phone Number Dialog:
- Generate a random valid UAE number: format `5XXXXXXXX` (9 digits starting with 5)
- Type the 9-digit suffix into the input
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971<generated-suffix>"` (replace with actual number) — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe".

**Step 5 — Post-subscribe Billing Page checks**

After clicking Subscribe, use `browser_wait_for` for each — no snapshot needed for text assertions:
- `browser_wait_for text="Your qlub account is created!"` — waits and verifies alert appeared
- `browser_wait_for text="-30.00"` — verifies qlub plus discount row
- `browser_wait_for text="Pay full bill"` — verifies discount applied
- `browser_wait_for text="<original − 30>"` — verifies Payable Amount decreased
- To check Subscription Checkbox `[checked]` state: `browser_evaluate: document.querySelector('[role="checkbox"]').getAttribute('aria-checked') === 'true'`

**Step 6 — Enter card details and pay with wrong 3DS password**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

On the 3D Secure dialog, enter an incorrect password (e.g. `WrongPass`). Take a fresh snapshot after typing (iframe re-renders invalidate refs), then click "Continue".

After clicking "Continue", **wait 6 seconds** (`browser_wait_for time=6`). Then take a snapshot.

**Step 7 — Payment Unsuccessful page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was unsuccessful!"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Please try again"`
- `browser_wait_for text="Failed"` — badge inside transaction card
- `browser_wait_for text="Try Again"`
- `browser_wait_for text="Back to home"`

**Step 7a — DB Verification (no subscription row after failed payment)**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

Verify that **no row** exists where `module_cat = "subscription"`. If such a row exists, log: FAIL — Expected no subscription row before successful payment, found `status: X`.

This check is a **non-blocker** — log and continue.

**Step 8 — Click Try Again**

Take a snapshot to get the `"Try Again"` ref, then click it. `browser_wait_for text="Payable amount"` — confirms the Billing Page loaded.

**Step 9 — Verify discount is still applied after Try Again**

Use `browser_wait_for` to confirm discount persisted — no snapshot needed for text assertions:
- `browser_wait_for text="-30.00"` — verifies qlub plus discount row still applied
- `browser_wait_for text="Pay full bill"` — verifies discount is active
- To check Subscription Checkbox `[checked]` state: `browser_evaluate: document.querySelector('[role="checkbox"]').getAttribute('aria-checked') === 'true'`
- Take a snapshot to confirm card number field is empty (ready for re-entry) — get refs for card fields

**Step 10 — Pay with correct 3DS password**

Enter card details again (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes, then wait for `"Payment was successful"`.

**Step 11 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with Payable Amount − 30) — verifies the amount
- `browser_wait_for text="You've saved 30.00 on this bill"`
- `browser_wait_for text="Congratulations!"`

**Step 11a — DB Verification**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "active"`
- `"subscription_type": "General"`

Log expected vs. actual if either fails (non-blocker).

---

### Scenario 3 — Existing User Login via Subscription Checkbox

**Goal:** A user who is already a qlub+ subscriber arrives at the billing page as a guest (not logged in). They use the Subscription Checkbox — normally intended for new users — to log in. The system detects the existing subscription, shows a "You are already subscribed" toast, and applies the 5% general discount automatically. The user then pays and the confirmation page is verified.

**Tables used:** Table 3

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 3 URL.

**Step 1 — Navigate to Billing Page**

`browser_wait_for text="Login"` — confirms user is not logged in. Then click "Pay now".

**Step 2 — Read Payable Amount**

On the Billing Page, read and store the **Payable Amount** shown in the `"Payable amount"` section (e.g. `180.00`). This will be used to calculate the expected 5% discount.

Calculate expected discount: `payableAmount × 0.05`, rounded to 2 decimal places (e.g. `180.00 × 0.05 = 9.00`).

**Step 3 — Open Subscription Dialog**

Click the Subscription Checkbox. Use `browser_wait_for` to verify dialog content — no snapshot needed for text assertions:
- `browser_wait_for text="Only 20 monthly"`
- `browser_wait_for text="Save up to 30% per bill"`
- `browser_wait_for text="30"` — verifies Subscribe button price

Take a snapshot only to get the ref for clicking `"Subscribe & Save"`.

**Step 4 — Enter Existing User Number**

Click "Subscribe & Save". On the Phone Number Dialog:
- Type `507391824` (the existing subscribed user's 9-digit suffix)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs.

**Step 5 — Subscribe and handle "Already Subscribed" toast**

Click "Subscribe".

After clicking, use `browser_wait_for` — do NOT take a snapshot immediately:
- `browser_wait_for text="You are already subscribed"` — waits and verifies the toast appeared (non-blocker failure if timeout)
- `browser_wait_for text="OK"` — waits and verifies the OK button is visible

Take a snapshot to get the OK button ref, then click it to dismiss the alert.

**Step 6 — Post-login Billing Page checks**

After dismissing the alert, use `browser_wait_for` for each — no snapshot needed for text assertions:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` (replace X with calculated 5%, e.g. `-9.00`) — verifies qlub plus discount row
- `browser_wait_for text="Pay full bill"` — verifies discount applied
- `browser_wait_for text="<original − X>"` (e.g. `"171.00"`) — verifies Payable Amount decreased
- To check Subscription Checkbox `[checked]` state: `browser_evaluate: document.querySelector('[role="checkbox"]').getAttribute('aria-checked') === 'true'`

**Step 7 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 8 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with original − X, e.g. `"171.00"`) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

---

### Scenario 4 — Existing User Login via Login Button

**Goal:** An existing qlub+ subscriber arrives at the billing page as a guest. They log in using the **"Login now" button** (the dedicated login entry point on the billing page, separate from the subscription checkbox flow). After logging in, the 5% general discount is applied automatically — no toast message expected in this flow. The user pays and the confirmation page is verified.

**Tables used:** Table 4

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 4 URL.

**Step 1 — Navigate to Billing Page**

`browser_wait_for text="Login"` — confirms user is not logged in. Then click "Pay now".

**Step 2 — Read Payable Amount**

On the Billing Page, read and store the **Payable Amount** shown in the `"Payable amount"` section (e.g. `180.00`). This is the pre-discount amount.

Calculate expected discount: `payableAmount × 0.05`, rounded to 2 decimal places.

**Step 3 — Log in via "Login now" button**

Click the `"Login now"` button (located below the subscription checkbox, inside the "Already a qlub+ member?" section).

On the Phone Number Dialog:
- Type `507391824` (the existing subscribed user's 9-digit suffix)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe".

**Step 4 — Post-login Billing Page checks**

No toast is expected in this flow. After login, use `browser_wait_for` for each — no snapshot needed for text assertions:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` (replace X with calculated 5%) — verifies qlub plus discount row
- `browser_wait_for text="Pay full bill"` — verifies discount applied
- `browser_wait_for text="<original − X>"` — verifies Payable Amount decreased
- To check Subscription Checkbox `[checked]` state: `browser_evaluate: document.querySelector('[role="checkbox"]').getAttribute('aria-checked') === 'true'`

**Step 5 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 6 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with original − X) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

---

### Scenario 5 — No Subscription After Split

**Goal:** Verify that the subscription checkbox and "Login now" banner are hidden after the user splits the bill using "Divide the bill equally". No payment is made — the scenario ends after verifying the billing page state.

**Tables used:** Table 5

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 5 URL.

**Step 1 — Navigate to Billing Page**

After the page loads, click "Pay now".

**Step 2 — Verify subscription elements are present**

Before splitting, use `browser_wait_for` to confirm the subscription section is visible:
- `browser_wait_for text="Login now"` — confirms login button present
- `browser_wait_for text="Already a qlub+ member?"` — confirms section present

**Step 3 — Split the bill**

Click the `"Split bill"` button. A bottom sheet opens with three split options.

Select `"Divide the bill equally"` by clicking its `"Select"` button.

A confirmation bottom sheet appears. Click the `"Confirm"` button.

**Step 4 — Verify subscription elements are gone**

After confirming the split:
- `browser_wait_for text="Edit split"` — confirms the split is applied and the button replaced "Split bill"
- For absence checks: `browser_evaluate: !document.body.textContent.includes('Login now')` — log pass/fail
- For absence checks: `browser_evaluate: !document.body.textContent.includes('Already a qlub+ member?')` — log pass/fail

**Step 5 — Remove the split**

Click the `"Edit split"` button. The "Divide the bill equally" confirmation bottom sheet opens again.

Click `"Remove split"` button inside the bottom sheet.

**Step 6 — Verify subscription elements reappear**

After removing the split, use `browser_wait_for` to confirm elements are back — no snapshot needed:
- `browser_wait_for text="Login now"` — confirms login button reappeared
- `browser_wait_for text="Already a qlub+ member?"` — confirms section reappeared
- `browser_wait_for text="Split bill"` — confirms Split bill button is restored

---

### Scenario 6 — No Split After Login

**Goal:** Verify that the "Split bill" button is hidden after an existing qlub+ subscriber logs in via the "Login now" button. Split is not permitted for subscribed users. No payment is made.

**Tables used:** Table 6

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 6 URL.

**Step 1 — Navigate to Billing Page**

After the page loads, click "Pay now".

**Step 2 — Verify Split bill button is present before login**

`browser_wait_for text="Split bill"` — confirms button is visible before logging in.

**Step 3 — Log in via "Login now" button**

Click `"Login now"`. On the Phone Number Dialog, type `507391824` and click "Receive Code" (or "Continue").

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown. Enter OTP `1`, `2`, `3`, `4`, `5`. Click "Continue" (or "Subscribe").

**Step 4 — Verify Split bill button is gone**

After login:
- `browser_wait_for text="Pay full bill"` — confirms discount is applied and replaces Split bill
- Absence check: `browser_evaluate: !document.body.textContent.includes('Split bill')` — log pass/fail

**Step 5 — Log out via Burger Menu**

Click the Burger Menu button (icon-only button, top-right). The burger menu opens.

Click `"Log out"`. The Logout Confirmation Dialog appears.

Click `"Log out"` inside the dialog to confirm. The user is redirected to the Landing Page.

**Step 6 — Navigate back to Billing Page**

`browser_wait_for text="Login"` — confirms user is logged out. Click `"Pay now"`.

**Step 7 — Verify Split bill button is restored**

Use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Split bill"` — confirms button is restored
- `browser_wait_for text="Login now"` — confirms subscription banner is restored

---

### Scenario 7 — Tip is Not Included in Discount (after login)

**Goal:** Verify that adding a tip does not affect the qlub+ discount amount. An existing subscriber logs in via the "Login now" button, the 5% general discount is applied, the discount amount is recorded, then a tip is selected — and the discount amount is confirmed to be unchanged.

**Tables used:** Table 7

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 7 URL.

**Step 1 — Navigate to Billing Page**

After the page loads, click "Pay now".

**Step 2 — Read Payable Amount**

On the Billing Page, read and store the **Payable Amount** shown in the `"Payable amount"` section (e.g. `180.00`). This is the pre-discount amount.

Calculate expected discount: `payableAmount × 0.05`, rounded to 2 decimal places.

**Step 3 — Log in via "Login now" button**

Click the `"Login now"` button (inside the "Already a qlub+ member?" section).

On the Phone Number Dialog:
- Type `507391824` (the existing subscribed user's 9-digit suffix)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe".

**Step 4 — Read and store the discount amount**

After login:
- `browser_wait_for text="qlub plus discount"` — waits and verifies the discount row appeared
- Take a snapshot to read and store the actual discount amount (e.g. `-9.00`) — this is the **pre-tip discount value** used for comparison in Step 6

**Step 5 — Select a tip**

In the tip section, click the `"10.00"` button (default tip — use a different value only if the scenario explicitly specifies one).

**Step 6 — Verify discount amount is unchanged**

After selecting the tip, use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="<stored discount amount>"` (e.g. `browser_wait_for text="-9.00"`) — confirms the discount value has not changed after the tip was added

---

### Scenario 8 — Tip is Not Included in Discount (before login)

**Goal:** Verify that a tip selected before login remains active after login, and that the qlub+ discount applied upon login is not affected by the pre-selected tip.

**Tables used:** Table 8

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 8 URL.

**Step 1 — Navigate to Billing Page**

After the page loads, click "Pay now".

**Step 2 — Select a tip before login**

In the tip section, click the `"10.00"` button (default tip — use a different value only if the scenario explicitly specifies one).

Use `browser_evaluate: document.querySelector('[data-selected="true"]') !== null` or similar to confirm the tip button is in a selected/active state — log pass/fail.

**Step 3 — Log in via "Login now" button**

Click the `"Login now"` button (inside the "Already a qlub+ member?" section).

On the Phone Number Dialog:
- Type `507391824` (the existing subscribed user's 9-digit suffix)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe".

**Step 4 — Verify tip is still selected after login**

After login:
- `browser_wait_for text="qlub plus discount"` — waits for discount to be applied after login
- Use `browser_evaluate` to confirm the `"10.00"` tip button is still selected/active — log pass/fail (visual state check requires evaluate, not browser_wait_for)
- Take a snapshot to read the `"You pay"` amount and confirm it reflects both discount and tip

**Step 5 — Verify discount amount is not affected by the tip**

Use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="<expected discount>"` (e.g. `browser_wait_for text="-9.00"` where 9.00 = payableAmount × 0.05) — confirms discount equals 5% of pre-tip, pre-login payable amount and has not been inflated by the tip

---

### Scenario 9 — Subscription with Qlub Login

**Goal:** An existing qlub+ subscriber logs in via the **top "Login" button** (Club login) on the Landing Page — before navigating to the billing page. After login, they click "Pay now" and land on the Billing Page where the 5% general discount is already applied automatically. No extra login step is needed on the billing page. The user pays and the confirmation page is verified.

**Tables used:** Table 9

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to Table 9 URL.

**Step 1 — Log in via top Login button on Landing Page**

`browser_wait_for text="Login"` — confirms user is not logged in. Click the `"Login"` button in the top-right corner.

On the Phone Number Dialog:
- Type `507391824` (the existing subscribed user's 9-digit suffix)
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971507391824"` — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe" (or "Continue").

**Step 2 — Verify logged-in state on Landing Page**

After login, use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Pay now"` — confirms Pay now button still visible
- Absence check for Login button: `browser_evaluate: !document.body.textContent.includes('Login')` — log pass/fail (profile icon replaced it)

**Step 3 — Navigate to Billing Page**

Click "Pay now". `browser_wait_for text="Payable amount"` — confirms the Billing Page loaded.

**Step 4 — Read Payable Amount and verify discount is applied**

Take a snapshot to read and store the **Payable Amount**. Calculate expected discount: `payableAmount × 0.05`, rounded to 2 decimal places.

Then use `browser_wait_for` for each — no further snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` — verifies qlub plus discount row
- `browser_wait_for text="<original − X>"` — verifies Payable Amount decreased
- `browser_wait_for text="Pay full bill"` — verifies discount applied

**Step 5 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 6 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with original − X) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

---

### Scenario 10 — New Standalone Subscriber + Cancel Subscription

**Goal:** A brand-new user visits a Standalone QR landing page, sees the subscription banner, and completes the Standalone subscription flow: login via OTP, pays 1 AED to activate the subscription (with 3DS), lands on the "Welcome to qlub+" screen, then clicks "Pay the Bill" to return to the Landing Page where the general discount banner is now visible. The user proceeds to the Billing Page, confirms the discount is applied, pays the bill, and the confirmation page is verified. Finally, the user navigates to Manage Subscription, cancels the subscription, and a DB verification confirms the status is changed to `"suspended"`.

**Tables used:** SS Table 1 — staging: Table 11 (`https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/6d55f45b13`) / dev7: Table 11 (`https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/20ab34b4f4`) / dev6: Table 11 (`https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/11/_/_/b9ced8f2ba`)

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to SS Table 1 URL.

**Step 1 — Read bill amount (before login)**

After the page loads, read the bill amount from the `"Pay now"` button text on the Landing Page (e.g. `"Pay now 147.00"` → `147.00`). Store this value.

Calculate expected discount: `billAmount × 0.05`, rounded to 2 decimal places (e.g. `147.00 × 0.05 = 7.35`).

**Step 2 — Verify Standalone subscription banner on Landing Page**

The banner is image-based and **not in the accessibility tree** — verify via `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null` and log pass/fail. Do not use screenshot for this check.

**Step 3 — Open Subscription Page**

Click the banner via `browser_evaluate`: `document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root').click()`. `browser_wait_for text="Subscribe & Save"` — confirms navigation to `/subscription/introduction`.

**Step 4 — Subscribe with a new UAE number**

Click the `"Subscribe & Save"` button. On the Phone Number Dialog:
- Generate a random valid UAE number: format `5XXXXXXXX` (9 digits starting with 5)
- Type the 9-digit suffix into the input
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971<generated-suffix>"` (replace with actual number) — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5` into the five separate inputs. Click "Subscribe" (or "Continue").

**Step 5 — Standalone card payment screen**

After OTP, use `browser_wait_for` to confirm the payment screen appeared — no snapshot needed for text assertions:
- `browser_wait_for text="A ₿ 1 charge will be made and refunded to verify your card."`
- `browser_wait_for text="<generated phone number>"` — verifies phone number is shown

Take a snapshot to get refs for the card fields.

Enter card details:
- Card Number: `4242 4242 4242 4242` (field inside Checkout.com iframe, placeholder `"1234 1234 1234 1234"`)
- Expiry Date: `1230` (single `"MM/YY"` field)
- Security Code: `444`

Click `"Subscribe Now"`.

**Step 6 — 3D Secure**

Complete 3DS with `Checkout1!` per Execution Notes, then wait for `"Welcome to qlub+"`.

**Step 7 — Welcome to qlub+ screen**

Use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Welcome to qlub+"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Your 7 days free trial is active now!"`
- `browser_wait_for text="Pay the Bill"`

Take a snapshot to get the ref, then click `"Pay the Bill"`.

**Step 7a — DB Verification (post 1 AED payment)**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "active"`
- `"subscription_type": "Standalone"`

Log expected vs. actual if either assertion fails (non-blocker). Then click `"Pay the Bill"`.

**Step 8 — Landing Page: discount banner replaces subscription banner**

After clicking "Pay the Bill", use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5% from Step 1) — confirms discount banner appeared
- `browser_wait_for text="Pay the bill to apply the discount"`
- Absence check for subscription banner: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') === null` — log pass/fail

**Step 9 — Navigate to Billing Page and verify discount**

Click "Pay now". Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` — verifies qlub plus discount row
- `browser_wait_for text="<bill amount − X>"` — verifies Payable Amount decreased
- `browser_wait_for text="Pay full bill"` — verifies discount applied

**Step 10 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 11 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with bill amount − X) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

**Step 11a — DB Verification**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "active"`
- `"subscription_type": "Standalone"`

Log expected vs. actual if either assertion fails (non-blocker).

---

#### Part 2 — Cancel Subscription

**Step 12 — Navigate to Manage Subscription**

Click the Burger Menu button (icon-only button, top-right corner of the confirmation page). The burger menu opens.

Click `"Manage subscription"`. The Manage Subscription page loads.

**Step 13 — Cancel subscription**

Click the `"Cancel subscription"` button.

The cancellation reason screen appears. `browser_wait_for text="Confirm cancellation"` — confirms the screen loaded. Take a snapshot to get the first checkbox ref, then check it.

`browser_wait_for text="Confirm cancellation"` — button should now be enabled. Take a snapshot to get its ref, then click it.

**Step 14 — Confirm cancellation bottom sheet**

Use `browser_wait_for` to confirm both buttons are visible before clicking:
- `browser_wait_for text="No, keep my subscription"`
- `browser_wait_for text="Yes, cancel my subscription"`

Take a snapshot to get the ref, then click `"Yes, cancel my subscription"`.

**Step 15 — Verify cancellation success**

`browser_wait_for text="cancelled"` — verifies success toast; if not found, try `browser_wait_for text="unsubscribed"`. No snapshot needed.

**Step 16 — DB Verification (post-cancellation)**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "suspended"`

Log expected vs. actual if the assertion fails (non-blocker).

---

### Scenario 11 — Standalone Banner/Subscription Page Resilience + New User Subscribe

**Goal:** Verify that the Standalone subscription banner and Subscription Page remain accessible across multiple open/close cycles. A new user logs in, dismisses the 1 AED payment screen without subscribing, and the system correctly shows the banner again (user is logged in but not yet subscribed). On a second attempt the user completes the 1 AED payment, the discount banner replaces the subscription banner, and the full payment flow is verified.

**Tables used:** SS Table 2 — staging: Table 12 (`https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/0562f7d18c`) / dev7: Table 12 (`https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/cd193aaa07`) / dev6: Table 12 (`https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/12/_/_/bd00290186`)

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to SS Table 2 URL.

**Step 1 — Verify Standalone banner on Landing Page**

`browser_wait_for text="Pay now"` — confirms Landing Page loaded. Read the bill amount from the `"Pay now"` button text (e.g. `"Pay now 147.00"` → `147.00`) — take a snapshot to extract this value. Calculate expected discount: `billAmount × 0.05`, rounded to 2 decimal places. Verify subscription banner is present: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null` — log pass/fail.

**Step 2 — Open / close cycle 1**

Click the banner using `browser_evaluate`: `document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root').click()`. Use `browser_wait_for text="Subscribe & Save"` to confirm the Subscription Page opened — no snapshot needed. Take a snapshot to get the Close Button ref, then click it. Use `browser_wait_for text="Pay now"` to confirm Landing Page is shown again. Verify banner still present: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null`.

**Step 3 — Open / close cycle 2**

Click the banner again (same `browser_evaluate` method). `browser_wait_for text="Subscribe & Save"` to confirm open. Take a snapshot to get Close Button ref, click it. `browser_wait_for text="Pay now"` to confirm back on Landing Page. Verify banner still present: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null`.

**Step 4 — Open Subscription Page (third time) and start subscribe flow**

Click the banner a third time (same `browser_evaluate` method). Verify the Standalone Subscription Page opens.

Click the `"Subscribe & Save"` button. Because the user is not logged in, the Phone Number Dialog appears.

**Step 5 — Log in with a new UAE number**

On the Phone Number Dialog:
- Generate a random valid UAE number: format `5XXXXXXXX` (9 digits starting with 5)
- Type the 9-digit suffix into the input
- Click "Receive Code"

On the OTP Dialog, `browser_wait_for text="+971<generated-suffix>"` (replace with actual number) — confirms correct number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5`. Click "Subscribe" (or "Continue").

**Step 6 — 1 AED payment screen appears — dismiss it**

After OTP success, use `browser_wait_for` to confirm the payment screen appeared:
- `browser_wait_for text="A ₿ 1 charge will be made and refunded to verify your card."`
- `browser_wait_for text="<generated phone number>"` — verifies phone shown

Take a snapshot to get the close/back button ref on the bottom sheet, then dismiss it without entering card details.

**Step 7 — Landing Page: banner still visible for logged-in but unsubscribed user**

After dismissing the payment screen:
- `browser_wait_for text="Pay now"` — confirms Landing Page is shown
- Subscription banner still present: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null` — log pass/fail
- Discount banner absent: `browser_evaluate: !document.body.textContent.includes('You save')` — log pass/fail

**Step 8 — Reopen Subscription Page and verify Subscribe button**

Click the banner via `browser_evaluate` (same method as above). `browser_wait_for text="Subscribe & Save"` — confirms page opened and button is visible. No snapshot needed.

**Step 9 — Click Subscribe — goes directly to 1 AED payment screen (no phone input)**

Click the `"Subscribe & Save"` button. Because the user is already logged in, the Phone Number Dialog is skipped. Use `browser_wait_for` to confirm the payment screen appeared directly:
- `browser_wait_for text="A ₿ 1 charge will be made and refunded to verify your card."`
- `browser_wait_for text="<generated phone number>"` — verifies correct phone shown

Take a snapshot to get refs for card fields.

**Step 10 — Complete the 1 AED payment**

Enter card details:
- Card Number: `4242 4242 4242 4242` (Checkout.com iframe, placeholder `"1234 1234 1234 1234"`)
- Expiry Date: `1230` (single `"MM/YY"` field)
- Security Code: `444`

Click `"Subscribe Now"`.

**Step 11 — 3D Secure**

Complete 3DS with `Checkout1!` per Execution Notes, then wait for `"Welcome to qlub+"`.

**Step 12 — Welcome to qlub+ screen**

Use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Welcome to qlub+"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Your 7 days free trial is active now!"`
- `browser_wait_for text="Pay the Bill"`

Take a snapshot to get the ref, then click `"Pay the Bill"`.

**Step 13 — Landing Page: discount banner replaces subscription banner**

After clicking "Pay the Bill", use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5% from Step 1) — confirms discount banner appeared
- `browser_wait_for text="Pay the bill to apply the discount"`
- Absence check for subscription banner: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') === null` — log pass/fail

**Step 14 — Navigate to Billing Page and verify discount**

Click "Pay now". Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="Pay the bill to apply the discount"`
- `browser_wait_for text="-X"` — verifies qlub plus discount row
- `browser_wait_for text="<bill amount − X>"` — verifies Payable Amount decreased
- `browser_wait_for text="Pay full bill"` — verifies discount applied

**Step 15 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay".

Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 16 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"` — verifies the label
- `browser_wait_for text="Y"` (replace Y with bill amount − X) — verifies the amount
- `browser_wait_for text="You've saved X on this bill"` (replace X with calculated 5%)

**Step 16a — DB Verification**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 5.

From the returned rows, find the row where `module_cat = "subscription"` and verify:
- `"status": "active"`
- `"subscription_type": "Standalone"`

Log expected vs. actual if either assertion fails (non-blocker).

---

### Scenario 12 — Standalone 3DS Failure: Wrong Password × 3 → Card Verification Failed

**Goal:** Verify that entering an incorrect 3DS password three consecutive times causes the 1 AED Standalone subscription payment to fail, shows the "Card Verification Failed!" screen, the user is NOT subscribed (confirmed via DB), and clicking "Try again" redirects the user back to the 1 AED payment screen.

**Tables used:** SS Table 3 — staging: Table 13 (`https://app-staging.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/1741580c50`) / dev7: Table 13 (`https://app-dev7.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/b92d1db193`) / dev6: Table 13 (`https://app-dev6.qlub.cloud/qr/ae/furkanSubscriptionAutomation/13/_/_/0225dc6bd5`)

---

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to SS Table 3 URL.

**Step 1 — Verify Standalone banner on Landing Page**

After the page loads: `browser_evaluate: document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root') !== null` — log pass/fail. No screenshot needed.

**Step 2 — Open Subscription Page**

Click the banner via `browser_evaluate`: `document.querySelector('[role="button"].styles-module-scss-module__iz-GHG__root').click()`. `browser_wait_for text="Subscribe & Save"` — confirms navigation to `/subscription/introduction`.

**Step 3 — Click Subscribe & Save**

Click the `"Subscribe & Save"` button. Because the user is not logged in, the Phone Number Dialog appears.

**Step 4 — Log in with a new UAE number**

On the Phone Number Dialog:
- Generate a random valid UAE number: format `50XXXXXXX` (9 digits starting with 50), e.g. `502345679`
- Enter the number and accept the Terms & Conditions checkbox
- Click "Receive Code"

On the OTP Dialog, verify the generated phone number is shown.

Enter OTP `1`, `2`, `3`, `4`, `5`. Click "Subscribe".

**Step 5 — 1 AED payment screen**

After OTP, use `browser_wait_for` to confirm the payment screen appeared:
- `browser_wait_for text="A ₿ 1 charge will be made and refunded to verify your card."`
- `browser_wait_for text="<generated phone number>"`

Take a snapshot to get refs for card fields.

Enter card details:
- Card Number: `4242 4242 4242 4242`
- Expiry Date: `1230` (MM/YY field)
- Security Code: `444`

Click `"Subscribe Now"`.

**Step 6 — 3DS: wrong password attempt 1**

A 3D Secure dialog appears. Enter an incorrect password (e.g. `WrongPass1`). Take a fresh snapshot after typing, then click "Continue".

Wait 6 seconds (`browser_wait_for time=6`). Take a snapshot:
- If the 3DS dialog reappears (retry prompt) → proceed to attempt 2.
- If the failure page appears immediately → skip to Step 8.

**Step 7 — 3DS: wrong password attempts 2 and 3**

Repeat the incorrect password entry two more times (total of 3 failed attempts). Each time:
- Enter incorrect password
- Take a fresh snapshot after typing
- Click "Continue"
- Wait 6 seconds and take a snapshot

After the third failed attempt, the 3DS flow should terminate and the app should redirect to the Card Verification Failed screen.

**Step 8 — Card Verification Failed screen**

Use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Card Verification Failed!"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="We couldn't verify your card details, so your subscription wasn't activated. Please try again."`
- `browser_wait_for text="Try again"`

**Step 8a — DB Verification (no subscription row)**

Call `get_customer_mapping_by_phone` using the phone number generated in Step 4.

Verify that **no row** exists where `module_cat = "subscription"`. If such a row exists, log: FAIL — Expected no subscription row, found `status: X`.

This check is a **non-blocker** — log and continue.

**Step 9 — Click Try again → redirects to 1 AED payment screen**

Take a snapshot to get the `"Try again"` ref, then click it. Use `browser_wait_for` to confirm redirect:
- `browser_wait_for text="Subscribe Now"` — confirms user is on the 1 AED payment screen again
- Take a snapshot to confirm card fields are empty and ready for new input

---

### Scenario 13 — Cap Limit: General Discount Usage Cap (3 per Week)

**Goal:** The `subscriptionAutomationCapLimit` restaurant is a newly created restaurant configured with a **weekly discount cap of 3 uses** for General subscribers (the cap renews after 7 days — renewal behavior is covered in a separate future scenario, not here). An existing General subscriber logs in and pays on three different Cap Limit tables (CL Table 1, 2, 3), receiving the general discount each time. After each payment, the auth/profile API response is inspected (via captured network traffic) to confirm `totalDiscountsUsedInCurrentPeriod` increments 1 → 2 → 3. The user then goes to a 4th table (CL Table 4) and it is verified that the discount is **not applied and not allowed** — the cap has been reached. CL Table 5 remains a spare for now.

**Tables used:** CL Table 1, CL Table 2, CL Table 3 (discounted payments), CL Table 4 (cap-reached verification) — dev6 only for now. CL Table 5 spare.

**Auth/profile API check:** During Step 1's payment flow, use `browser_network_requests` (or `browser_network_request`) to locate the auth/profile API call (response shape includes `profile.totalDiscountsUsedInCurrentPeriod`, `profile.discountSavings`, `profile.phoneNumber`, etc. — see example payload below). Once the matching request URL pattern is identified, reuse the same lookup after each subsequent payment to read the updated count. This check is a **non-blocker** — log expected vs. actual if it fails Log and continue.

```json
{
    "profile": {
        "id": "b24d477a-7142-449e-8ae4-f56cb7a1c8d6",
        "memberID": "00135-e23be9fe-4943-4f98-8d6d-4c914e5d6368",
        "accountID": "",
        "name": "",
        "email": "",
        "phoneNumber": "+971503482137",
        "createdOn": "2026-07-27T09:16:44Z",
        "accountBalance": { "monetary": 0, "nonMonetary": 0 },
        "pointsEarned": 0,
        "pointsSpent": 0,
        "expiringPoints": 0,
        "subscriptionExpenses": 0,
        "discountSavings": 16.25,
        "totalDiscountsUsedInCurrentPeriod": 3,
        "extras": {
            "lastMobileLoginDate": "2026-07-27T09:16:43Z",
            "lastCashbackEnabledDate": null,
            "cashbackExpiredDate": null
        },
        "lifetimeSavings": 0
    }
}
```

---

#### Part 1 — CL Table 1: First Discounted Payment (count → 1)

**Setup:** Clear storage (`localStorage.clear(); sessionStorage.clear();`) then navigate to CL Table 1 URL (dev6).

**Step 1 — Navigate to Billing Page and log in**

`browser_wait_for text="Login"` — confirms user is not logged in. Click `"Pay now"`.

Read and store the **Payable Amount**. Calculate expected discount: `payableAmount × 0.05`, rounded to 2 decimal places.

Click the `"Login now"` button (inside the "Already a qlub+ member?" section). On the Phone Number Dialog, type `507391824` (existing General subscriber — rotate per the General subscribers list if rate-limited) and click "Receive Code".

On the OTP Dialog, `browser_wait_for text="+971507391824"`. Enter OTP `1`, `2`, `3`, `4`, `5`. Click "Subscribe".

**Step 2 — Verify discount applied**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="You save X on this bill"` (replace X with calculated 5%)
- `browser_wait_for text="-X"` — verifies qlub plus discount row
- `browser_wait_for text="Pay full bill"` — verifies discount applied
- `browser_wait_for text="<original − X>"` — verifies Payable Amount decreased

**Step 3 — Pay**

Enter card details (Visa test card: `4242 4242 4242 4242`, expiry `12/30`, CVV `444`). Click "Pay". Complete 3DS with `Checkout1!` per Execution Notes if it appears.

**Step 4 — Confirmation Page**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"`
- `browser_wait_for text="Y"` (replace Y with original − X)
- `browser_wait_for text="You've saved X on this bill"`

**Step 4a — Profile API Verification**

Use `browser_network_requests` to locate the auth/profile response for `+971507391824`. Verify:
- `"totalDiscountsUsedInCurrentPeriod": 1`

Log expected vs. actual if it fails (non-blocker).

---

#### Part 2 — CL Table 2: Second Discounted Payment (count → 2)

**Setup:** Same tab/session (do not clear storage — user stays logged in). Navigate to CL Table 2 URL.

**Step 5 — Navigate to Billing Page**

Click `"Pay now"`. Read and store the **Payable Amount**. Calculate expected discount: `payableAmount × 0.05`.

**Step 6 — Verify discount already applied (user is logged in)**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="-X"` (replace X with calculated 5%)
- `browser_wait_for text="Pay full bill"`
- `browser_wait_for text="<original − X>"`

**Step 7 — Pay**

Same card details and 3DS flow as Step 3.

**Step 8 — Confirmation Page**

Same checks as Step 4, with recalculated X/Y for this table's bill amount.

**Step 8a — Profile API Verification**

Verify `"totalDiscountsUsedInCurrentPeriod": 2` (non-blocker).

---

#### Part 3 — CL Table 3: Third Discounted Payment (count → 3, cap reached)

**Setup:** Same session. Navigate to CL Table 3 URL.

**Step 9 — Navigate to Billing Page, verify discount, pay** — repeat Steps 5–7 for CL Table 3.

**Step 10 — Confirmation Page** — repeat Step 4/8 checks with this table's bill amount.

**Step 10a — Profile API Verification**

Verify `"totalDiscountsUsedInCurrentPeriod": 3` (non-blocker).

---

#### Part 4 — CL Table 4: Cap Reached — Discount Not Applied

**Setup:** Same session (user still logged in). Navigate to CL Table 4 URL.

**Step 11 — Verify Weekly Eligible Limit Banner on Landing Page**

After the page loads, use `browser_wait_for` — no snapshot needed:
- `browser_wait_for text="Weekly eligible limit reached"` — gate: if this doesn't appear, the cap did not block correctly (non-blocker, but log clearly)
- `browser_wait_for text="You've used all eligible discounts for this week"`

**Step 12 — Navigate to Billing Page and verify discount is NOT applied**

Click `"Pay now"`. Read the **Payable Amount**.

Use `browser_wait_for`/`browser_evaluate` — no discount should appear despite the user being an active subscriber:
- Absence check: `browser_evaluate: !document.body.textContent.includes('You save')` — log pass/fail
- Absence check: `browser_evaluate: !document.body.textContent.includes('qlub plus discount')` — log pass/fail
- `browser_wait_for text="<full Payable Amount>"` — confirms amount is unchanged (no discount subtracted)
- Whatever the full-payment CTA is in this state (e.g. `"Pay fully"` / `"Pay full bill"`) — verify it reflects the undiscounted amount

**Step 13 — Pay full amount**

Enter card details. Click "Pay". Complete 3DS with `Checkout1!` if it appears.

**Step 14 — Confirmation Page — no savings shown**

Use `browser_wait_for` for each — no snapshot needed:
- `browser_wait_for text="Payment was successful"` — gate: if timeout, mark BLOCKER FAILURE
- `browser_wait_for text="Fully paid"`
- `browser_wait_for text="You paid"`
- `browser_wait_for text="<full Payable Amount>"` — confirms full price was charged
- Absence check: `browser_evaluate: !document.body.textContent.includes("You've saved")` — log pass/fail (no savings line should appear)

**Step 14a — Profile API Verification**

Verify `"totalDiscountsUsedInCurrentPeriod"` remains `3` (not incremented) — confirms the cap blocked a 4th discount. Log expected vs. actual (non-blocker).

---

## Regression Suite

_To be filled._

---

## Writing New Scenarios

_To be filled._
