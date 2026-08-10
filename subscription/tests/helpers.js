// ---------------------------------------------------------------------------
// Test card
// ---------------------------------------------------------------------------
export const CARD = {
  number: '4242 4242 4242 4242',
  expiry: '1230', // MM/YY, no separator — used by Checkout.com's single expiry field
  expiryMonth: '12', // used by Moneyhash's separate month/year fields
  expiryYear: '30',
  cvv: '444',
};

// ---------------------------------------------------------------------------
// randomUaePhoneSuffix
// Generates a fresh 9-digit UAE mobile suffix for new-user scenarios. Never
// reuse the returned suffix across scenarios that need a genuinely
// unregistered number.
//
// Only these 2-digit prefixes are real UAE mobile allocations (Etisalat:
// 50/52/54; du: 55/56; du/Virgin: 58) — confirmed live on 2026-08-07: a
// randomly generated "59..." number was rejected as invalid by the app.
// Every real working number we've captured so far (507391824, 523456789,
// 589012347, 502341987, 521234599, 509876543) also only ever used 50/52/58.
// Picking the 2nd digit fully at random (the old approach) could produce
// invalid prefixes like 51/53/57/59 — pick from this fixed set instead.
// ---------------------------------------------------------------------------
const UAE_MOBILE_PREFIXES = ['50', '52', '54', '55', '56', '58'];

export function randomUaePhoneSuffix() {
  const prefix = UAE_MOBILE_PREFIXES[Math.floor(Math.random() * UAE_MOBILE_PREFIXES.length)];
  const rest = Array.from({ length: 7 }, () => Math.floor(Math.random() * 10)).join('');
  return `${prefix}${rest}`;
}

// ---------------------------------------------------------------------------
// ensureLoggedOut
// `furkanSubscriptionAutomation`'s tables share a single mutable identity
// server-side — whichever phone number last completed a full OTP login is
// auto-logged-in on EVERY table, regardless of browser/cookies/storage.
// Clearing localStorage/sessionStorage/cookies does NOT reset this.
// Cheap-check-first: if the "Login" button is already visible, do nothing —
// only pay the cost of the full logout flow when the page is actually in a
// logged-in state (e.g. a previous test crashed before its own teardown).
// ---------------------------------------------------------------------------
export async function ensureLoggedOut(page) {
  const loginBtn = page.getByRole('button', { name: 'Login' });
  const burgerBtn = page.locator('[data-qa-id="burger"]');

  // isVisible() alone does NOT wait/retry — it's an instant check. Wait for
  // the landing page to actually finish rendering (either state) first.
  await Promise.race([
    loginBtn.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {}),
    burgerBtn.waitFor({ state: 'visible', timeout: 15000 }).catch(() => {}),
  ]);

  if (await loginBtn.isVisible()) return;

  await openBurgerMenu(page);
  const drawerLogoutBtn = page.getByRole('button', { name: 'Log out' });
  await drawerLogoutBtn.waitFor({ state: 'visible', timeout: 10000 });
  await drawerLogoutBtn.click();

  const confirmDialog = page.getByRole('dialog').filter({ hasText: 'Are you sure you want to log out?' });
  await confirmDialog.getByRole('button', { name: 'Log out' }).click();

  await loginBtn.waitFor({ state: 'visible', timeout: 15000 });
}

// ---------------------------------------------------------------------------
// logoutIfPossible
// Best-effort courtesy logout for afterEach — never throws, so a failure
// here never masks the real test result. This is NOT the safety net (that's
// ensureLoggedOut in beforeEach) — it just keeps the common case common.
// ---------------------------------------------------------------------------
export async function logoutIfPossible(page) {
  await ensureLoggedOut(page).catch(() => {});
}

// ---------------------------------------------------------------------------
// openBurgerMenu
// Resilient to Landing/Billing (data-qa-id="burger") vs. Confirmation page,
// which does not expose that attribute — on Confirmation, the menu icon is
// the second of two elements sharing the raw DOM id "#backBtn" (confirmed
// live; a duplicate-id quirk in the app itself, not a selector mistake).
// The fallback click has an explicit timeout — confirmed live 2026-08-08
// that without one, a page that fails to load at all (e.g. a genuine
// network hiccup) can leave this click waiting far longer than any test
// timeout should tolerate, since it has no element to ever find.
// ---------------------------------------------------------------------------
export async function openBurgerMenu(page) {
  const dataQaBurger = page.locator('[data-qa-id="burger"]');
  const appeared = await dataQaBurger
    .waitFor({ state: 'visible', timeout: 3000 })
    .then(() => true)
    .catch(() => false);
  if (appeared) {
    await dataQaBurger.click();
    return;
  }
  await page.locator('#backBtn').nth(1).click({ timeout: 10000 });
}

// ---------------------------------------------------------------------------
// subscribeViaCheckbox
// Subscribe flow starting from the Billing Page's Subscription Checkbox:
// checkbox -> Subscription info dialog -> phone -> OTP -> Subscribe.
//
// Works for BOTH a genuinely new phone number (welcome discount applies
// directly) and an already-subscribed existing number (the app shows a
// "You are already subscribed" toast with an OK button instead — confirmed
// live during Scenario 1 work, 2026-08-07/08 — after dismissing it, the
// General discount is applied the same way a returning subscriber sees it).
// Dismissing the toast is a no-op for the new-user path since it never
// appears there.
// ---------------------------------------------------------------------------
export async function subscribeViaCheckbox(page, phoneSuffix) {
  await page.locator('#invoiceElement').getByRole('checkbox').click();
  await page.getByRole('button', { name: 'Subscribe & Save' }).click();
  await fillPhoneAndRequestOtp(page, phoneSuffix);
  await fillOtpAndSubmit(page, 'Subscribe');

  const alreadySubscribed = page.getByText('You are already subscribed');
  const shown = await alreadySubscribed.waitFor({ state: 'visible', timeout: 8000 }).then(() => true).catch(() => false);
  if (shown) {
    await page.getByRole('button', { name: 'OK' }).click();
  }
}

// ---------------------------------------------------------------------------
// completeQlubLoginDialog
// Shared phone + OTP submission for the "Login to qlub" dialog — confirmed
// live 2026-08-09/10 this exact dialog is reused by BOTH the dedicated
// "Login now" button (Billing Page) and the top "Login" button (Landing and
// Billing Page, Club login): same title, same phone step submitting via
// "Continue" (not "Receive Code"), same OTP step submitting via "Continue"
// (not "Subscribe"). Callers just click their own trigger button first.
// ---------------------------------------------------------------------------
async function completeQlubLoginDialog(page, phoneSuffix) {
  const input = page.getByRole('textbox', { name: 'Mobile number' });
  await input.click();
  const validatePhone = page
    .waitForResponse((res) => res.url().includes('/validate_phone') && res.status() === 200, { timeout: 20000 })
    .catch(() => null);
  await input.pressSequentially(phoneSuffix, { delay: 80 });
  await validatePhone;
  await page.getByRole('button', { name: 'Continue' }).click({ timeout: 20000 });

  for (let i = 1; i <= 5; i++) {
    await page.getByRole('textbox', { name: `Please enter OTP character ${i}` }).fill(String(i));
  }
  await page.getByRole('button', { name: 'Continue' }).click();
}

// ---------------------------------------------------------------------------
// loginViaLoginButton
// Existing-subscriber login via the dedicated "Login now" button (inside the
// "Already a qlub+ member?" section on the Billing Page) — a separate entry
// point from the Subscription Checkbox. No "You are already subscribed"
// toast is shown on this path either (per SKILL.md), so none is handled here.
// ---------------------------------------------------------------------------
export async function loginViaLoginButton(page, phoneSuffix) {
  await page.getByRole('button', { name: 'Login now' }).click();
  await completeQlubLoginDialog(page, phoneSuffix);
}

// ---------------------------------------------------------------------------
// loginViaTopLoginButton
// Existing-subscriber login via the top "Login" button (Club login) —
// present on both the Landing Page and Billing Page. Confirmed live
// 2026-08-10: after this login, the Landing Page's "Login" button is
// replaced by the profile icon and "Pay now" stays visible; the General
// discount is then applied automatically once Billing Page is reached, no
// further login step needed there (per SKILL.md).
// ---------------------------------------------------------------------------
export async function loginViaTopLoginButton(page, phoneSuffix) {
  await page.getByRole('button', { name: 'Login' }).click();
  await completeQlubLoginDialog(page, phoneSuffix);
}

// Uses pressSequentially (not fill) — the "Receive Code" button only enables
// once /validate_phone resolves on keystroke, and fill() sets the DOM value
// without firing real input/keydown events, so the SDK never sees it and the
// button stays disabled forever. Confirmed live: fill() alone hangs here.
export async function fillPhoneAndRequestOtp(page, phoneSuffix) {
  const input = page.getByRole('textbox', { name: 'Mobile number' });
  await input.click();
  const validatePhone = page
    .waitForResponse((res) => res.url().includes('/validate_phone') && res.status() === 200, { timeout: 20000 })
    .catch(() => null);
  await input.pressSequentially(phoneSuffix, { delay: 80 });
  await validatePhone;
  await page.getByRole('button', { name: 'Receive Code' }).click({ timeout: 20000 });
}

// Valid OTP for the test environment is always 1-2-3-4-5, one digit per box.
export async function fillOtpAndSubmit(page, submitButtonName) {
  for (let i = 1; i <= 5; i++) {
    await page.getByRole('textbox', { name: `Please enter OTP character ${i}` }).fill(String(i));
  }
  await page.getByRole('button', { name: submitButtonName }).click();
}

// ---------------------------------------------------------------------------
// fillCardForm
// The card payment component appears to be lazy-mounted based on scroll
// position — confirmed live on 2026-08-07: every prior "hangs at the
// payment step" failure actually happened because the page stays scrolled
// to the top (discount banner) after OTP/subscribe, and the card iframe
// never gets created in the DOM at all until the page scrolls down to that
// section. This was previously misdiagnosed as a flaky gateway/redirect
// issue. Always scroll to the bottom before looking for card fields.
//
// Which payment gateway renders is NOT reliably tied to "first payment vs.
// repeat payment" — confirmed live: two different runs of the same "returning
// subscriber, General discount" step got Moneyhash once and Checkout.com
// once. Detect whichever gateway's fields actually appear at runtime instead
// of assuming. Returns 'checkout' or 'moneyhash' so callers/logs know which
// one ran, but callers should treat both as equally valid outcomes.
// ---------------------------------------------------------------------------
export async function fillCardForm(page, card = CARD) {
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

  const checkoutFrame = page.locator('[data-testid="card-number"]');
  const moneyhashFrame = page.locator('#card-number iframe');

  // Some renders show "Card and others" as a COLLAPSED payment-method row
  // (a checkmark, no visible fields) rather than pre-expanded — confirmed
  // live on 2026-08-09. Click it to expand if the fields aren't already
  // present; harmless no-op when they are (short wait, not a hard fail).
  const alreadyThere = await checkoutFrame
    .or(moneyhashFrame)
    .first()
    .waitFor({ state: 'visible', timeout: 3000 })
    .then(() => true)
    .catch(() => false);
  if (!alreadyThere) {
    const cardMethodRow = page.getByText('Card and others');
    const rowVisible = await cardMethodRow
      .waitFor({ state: 'visible', timeout: 3000 })
      .then(() => true)
      .catch(() => false);
    if (rowVisible) await cardMethodRow.click();
  }

  // Confirmed live on 2026-08-07: right after scrolling into view, the
  // "Payment method" section can still be showing grey skeleton
  // placeholders (and "You pay ₨0.00" not yet recalculated) — the real
  // card component/iframe hasn't mounted yet. 20s was occasionally not
  // enough; give it real headroom rather than assume it's instant.
  await checkoutFrame.or(moneyhashFrame).first().waitFor({ state: 'visible', timeout: 45000 });

  if (await checkoutFrame.isVisible().catch(() => false)) {
    await checkoutFrame.contentFrame().getByTestId('card-number').fill(card.number);
    await page.locator('[data-testid="card-expiry-date"]').contentFrame().getByTestId('card-expiry-date').fill(card.expiry);
    await page.locator('[data-testid="card-cvv"]').contentFrame().getByTestId('card-cvv').fill(card.cvv);
    return 'checkout';
  }

  await moneyhashFrame.contentFrame().getByRole('textbox').fill(card.number.replace(/\s/g, ''));
  await page.locator('#expiry-month iframe').contentFrame().getByRole('textbox').fill(card.expiryMonth);
  await page.locator('#expiry-year iframe').contentFrame().getByRole('textbox').fill(card.expiryYear);
  await page.locator('#cvv iframe').contentFrame().getByRole('textbox').fill(card.cvv);
  return 'moneyhash';
}

// ---------------------------------------------------------------------------
// payAndAwaitOutcome
// Fills the card form, clicks Pay, handles 3DS IF it appears (Moneyhash
// never shows it; Checkout.com doesn't always either — not reliably tied to
// first-vs-repeat payment, same caveat as fillCardForm above), then waits
// for the real outcome URL.
//
// KNOWN FLAKY BEHAVIOR (confirmed live, reproduced multiple times in two
// different visual forms — once as a "Completing your payment" holding
// screen with only a fallback link, once as the Pay button stuck in its
// loading state): the redirect after payment can hang after 3DS. Previously
// this helper avoided clicking the "Click here if you're not redirected
// automatically" link, on the theory that it breaks session context — but
// watching it live (2026-08-08) showed clicking it is the correct recovery:
// it completes the redirect. So click it if the holding screen appears.
//
// UNCONFIRMED ALTERNATIVE HYPOTHESIS (raised 2026-08-07, not yet verified):
// this restaurant's tables are backed by a dummy/fake POS that cycles
// orders rather than generating a fresh one instantly per visit. Repeatedly
// re-running tests against the same table in quick succession may exhaust
// its queued order, leaving nothing valid for Pay to actually process —
// which could look identical to a stuck gateway redirect from the outside.
// If this test is flaky again, check whether rotating tables per run or
// waiting between runs on the same table changes the failure rate before
// assuming it's the gateway/redirect.
//
// Mitigation either way: one bounded retry — if the outcome URL never
// arrives, reload the billing page (discount/session state persists across
// reload) and redo the whole fill+submit once more before failing for real.
// ---------------------------------------------------------------------------
export async function payAndAwaitOutcome(page, { password = 'Checkout1!', card = CARD, maxAttempts = 2 } = {}) {
  let lastError;
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      await fillCardForm(page, card);
      await page.getByRole('button', { name: 'Pay' }).click();

      const dialogFrame = page.locator('iframe[title="Embedded 3D Secure 2 Authentication"]');
      const need3ds = await dialogFrame.waitFor({ state: 'visible', timeout: 8000 }).then(() => true).catch(() => false);

      if (need3ds) {
        const threeDsFrame = dialogFrame.contentFrame().locator('iframe[name="cko-3ds2-iframe"]').contentFrame();
        await threeDsFrame.getByRole('textbox', { name: `Hint: ${password}` }).fill(password);
        await threeDsFrame.getByRole('button', { name: 'Continue' }).click();
      }

      // "Completing your payment" holding screen — click through it if it
      // appears (confirmed live 2026-08-08: this is the correct recovery,
      // not something to avoid).
      const stuckLink = page.getByRole('link', { name: 'Click here' });
      const stuck = await stuckLink.waitFor({ state: 'visible', timeout: 10000 }).then(() => true).catch(() => false);
      if (stuck) await stuckLink.click();

      // waitUntil: 'commit' — confirmed live on 2026-08-07: the app fires a
      // second navigation/reload right after landing on the outcome URL, so
      // the default waitUntil ('load') can hang even though the URL already
      // matched. We only care that the URL committed; the caller's own
      // "Payment was successful" text assertion is the real readiness check.
      await page.waitForURL(/invoice\/(success|pending)/, { timeout: 45000, waitUntil: 'commit' });
      return;
    } catch (err) {
      lastError = err;
      if (attempt < maxAttempts) await page.reload();
    }
  }
  throw lastError;
}

// ---------------------------------------------------------------------------
// submitWrongPasswordUntilFailure
// A single wrong 3DS password does NOT fail the payment — confirmed live on
// 2026-08-08: the same dialog re-renders in place showing "N attempt(s)
// remaining" and lets you retry. It takes 3 consecutive wrong attempts
// before the app gives up and navigates to the "Payment was unsuccessful!"
// page. This mirrors the already-documented Standalone 3DS rule (3 wrong
// attempts in a row), now confirmed for the regular subscription flow too.
// Call this AFTER clicking Pay (assumes the 3DS dialog is already open).
// ---------------------------------------------------------------------------
export async function submitWrongPasswordUntilFailure(page, { attempts = 3 } = {}) {
  const dialogFrame = page.locator('iframe[title="Embedded 3D Secure 2 Authentication"]');
  await dialogFrame.waitFor({ state: 'visible', timeout: 15000 });

  for (let i = 1; i <= attempts; i++) {
    const threeDsFrame = dialogFrame.contentFrame().locator('iframe[name="cko-3ds2-iframe"]').contentFrame();
    await threeDsFrame.getByRole('textbox', { name: 'Hint: Checkout1!' }).fill(`WrongPass${i}`);
    await threeDsFrame.getByRole('button', { name: 'Continue' }).click();

    // The nested 3DS iframe appears to remount between attempts — confirmed
    // live 2026-08-09: querying/filling too soon after Continue can target a
    // stale mid-transition frame with no visible effect (still showed the
    // previous "N attempt(s) remaining" state with an empty field). Confirm
    // the expected next state before moving on, rather than firing blind.
    const remaining = attempts - i;
    if (remaining > 0) {
      await dialogFrame
        .contentFrame()
        .locator('iframe[name="cko-3ds2-iframe"]')
        .contentFrame()
        .getByText(`${remaining} attempt(s) remaining`)
        .waitFor({ state: 'visible', timeout: 10000 });
    }
  }

  // Same "Completing your payment" stuck-redirect behavior seen after a
  // successful payment (see payAndAwaitOutcome) can also happen here, after
  // the final wrong attempt transitions to the failure page — confirmed
  // live 2026-08-09. The holding screen can take a while to even appear, so
  // poll for it across a few rounds instead of checking only once — a
  // single 10s check missed it entirely on one run because it hadn't
  // rendered yet.
  for (let round = 0; round < 3; round++) {
    if (/invoice\/(pending|success)/.test(page.url())) break;
    const stuckLink = page.getByRole('link', { name: 'Click here' });
    const stuck = await stuckLink.waitFor({ state: 'visible', timeout: 10000 }).then(() => true).catch(() => false);
    if (stuck) {
      await stuckLink.click();
      break;
    }
  }

  // Lands on an /invoice/pending URL that renders the FAILURE UI, not the
  // success UI — same URL shape as a real pending payment, just different
  // content. Caller must check page text to tell them apart.
  await page.waitForURL(/invoice\/(pending|success)/, { timeout: 30000, waitUntil: 'commit' });
}

// ---------------------------------------------------------------------------
// splitBillEqually / removeSplit
// Split bill -> Divide the bill equally -> Confirm (and the reverse: Edit
// split -> Remove split). Confirmed live 2026-08-09: clicking "Confirm" is
// intermittently flaky — the "Divide the bill equally" sheet can fail to
// close and the billing page stays unsplit even though the click registered
// (reproduced directly: same dialog DOM node re-queried right after the
// click still showed "Confirm", and a second click on it then succeeded
// immediately). Bounded retry, same mitigation style as payAndAwaitOutcome.
// ---------------------------------------------------------------------------
export async function splitBillEqually(page, { maxAttempts = 3 } = {}) {
  await page.getByRole('button', { name: 'Split bill' }).click();
  await page.getByRole('button', { name: 'Divide the bill equally' }).click();

  const confirmBtn = page.getByRole('button', { name: 'Confirm' });
  await confirmBtn.waitFor({ state: 'visible', timeout: 10000 });

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    await confirmBtn.click();
    const applied = await page
      .getByRole('button', { name: 'Edit split' })
      .waitFor({ state: 'visible', timeout: 10000 })
      .then(() => true)
      .catch(() => false);
    if (applied) return;
  }
  throw new Error('splitBillEqually: "Edit split" never appeared after confirming the split');
}

export async function removeSplit(page, { maxAttempts = 3 } = {}) {
  await page.getByRole('button', { name: 'Edit split' }).click();
  const removeBtn = page.getByRole('button', { name: 'Remove split' });
  await removeBtn.waitFor({ state: 'visible', timeout: 10000 });

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    await removeBtn.click();
    const removed = await page
      .getByRole('button', { name: 'Split bill' })
      .waitFor({ state: 'visible', timeout: 10000 })
      .then(() => true)
      .catch(() => false);
    if (removed) return;
  }
  throw new Error('removeSplit: "Split bill" never reappeared after removing the split');
}

// ---------------------------------------------------------------------------
// getQlubPlusDiscountText
// Reads the "qlub plus discount" row's amount (e.g. "-2.20"). Confirmed live
// 2026-08-09: the minus sign and the number are rendered in separate DOM
// nodes (both siblings of the "qlub plus discount" label, two levels up),
// so innerText comes back as "qlub plus discount\n\n-\n2.20" — strip
// whitespace before matching, or the sign and number won't concatenate.
// ---------------------------------------------------------------------------
export async function getQlubPlusDiscountText(page) {
  const label = page.getByText('qlub plus discount', { exact: true });
  await label.waitFor({ state: 'visible', timeout: 15000 });
  const rowText = await label.locator('../..').innerText();
  const match = rowText.replace(/\s+/g, '').match(/-\d+\.\d{2}/);
  if (!match) throw new Error(`Could not parse discount amount from row text: "${rowText}"`);
  return match[0];
}

// ---------------------------------------------------------------------------
// getLabeledAmountText
// Reads the amount next to a label that shares its immediate parent (e.g.
// "Payable amount", "Tip amount:", "You pay" — confirmed live 2026-08-09,
// one level up is enough for these; unlike "qlub plus discount", which needs
// getQlubPlusDiscountText's two-level lookup because of its extra sign span).
// ---------------------------------------------------------------------------
export async function getLabeledAmountText(page, labelText, { timeout = 15000 } = {}) {
  const label = page.getByText(labelText).first();
  await label.waitFor({ state: 'visible', timeout });

  const deadline = Date.now() + timeout;
  let rowText;
  do {
    rowText = await label.locator('..').innerText();
    const match = rowText.replace(/\s+/g, '').match(/-?\d+\.\d{2}/);
    if (match) return match[0];
    await page.waitForTimeout(200);
  } while (Date.now() < deadline);

  throw new Error(`Could not parse amount from row text: "${rowText}" (label: "${labelText}")`);
}

// ---------------------------------------------------------------------------
// Standalone subscription — composable pieces
// The image-based Landing Page banner selector below is confirmed live
// 2026-08-09/10 to still match SKILL.md's documented selector — it is NOT in
// the accessibility tree, so it must be located/clicked via evaluate. The
// banner isn't always in the DOM the instant the Landing Page's other
// elements render, so callers wait for it to exist before clicking.
// ---------------------------------------------------------------------------
const STANDALONE_BANNER_SELECTOR = '[role="button"].styles-module-scss-module__iz-GHG__root';

// A one-shot query can race the same late-mount timing seen in
// openStandaloneSubscriptionPage — poll briefly so a "not there yet" isn't
// mistaken for "not there". `expectPresent: false` skips the poll (an
// absence check has nothing to wait for — it's correct immediately after an
// action that's already confirmed to have removed the banner).
export async function standaloneBannerExists(page, { expectPresent = true, timeout = 5000 } = {}) {
  const check = () => page.evaluate((sel) => document.querySelector(sel) !== null, STANDALONE_BANNER_SELECTOR);
  if (!expectPresent) return check();

  const deadline = Date.now() + timeout;
  let found = await check();
  while (!found && Date.now() < deadline) {
    await page.waitForTimeout(200);
    found = await check();
  }
  return found;
}

// Opens the Standalone Subscription intro/checkout page from the Landing
// Page banner. Waits for "Subscribe & Save" (present whether this lands on
// the intro page for a guest or is skipped straight to it — see
// startStandaloneSubscribe for what happens next).
export async function openStandaloneSubscriptionPage(page) {
  await page.waitForFunction((sel) => document.querySelector(sel) !== null, STANDALONE_BANNER_SELECTOR, { timeout: 15000 });
  await page.evaluate((sel) => document.querySelector(sel).click(), STANDALONE_BANNER_SELECTOR);
  await page.getByText('Subscribe & Save').waitFor({ state: 'visible', timeout: 15000 });
}

// Closes the Subscription intro page (before clicking "Subscribe & Save")
// and returns to the Landing Page. Confirmed live 2026-08-10: this page can
// have a second, hidden stale close button left in the DOM from an earlier
// mount — the app doesn't always remove closed-dialog nodes (same quirk
// documented for the split-bill sheet) — so scope to the visible one.
export async function closeStandaloneSubscriptionPage(page) {
  await page.locator('button[class*="__close"]:visible').click();
  await page.getByRole('button', { name: /Pay now/ }).waitFor({ state: 'visible', timeout: 15000 });
}

// Dismisses the 1 AED card-verification screen without paying, returning to
// the Landing Page. Confirmed live 2026-08-10: this close icon is NOT a
// literal <button> tag (an ARIA role="button" wrapper instead), so its
// locator must omit the `button` tag prefix used elsewhere.
export async function dismissStandaloneCardPayment(page) {
  await page.locator('[class*="__close-icon"]').click();
  await page.getByRole('button', { name: /Pay now/ }).waitFor({ state: 'visible', timeout: 15000 });
}

// Clicks "Subscribe & Save" on the intro page. For a logged-out user this
// opens the Phone Number Dialog; for an already-logged-in user (e.g. after
// dismissing a prior attempt) it skips straight to the 1 AED payment screen
// — confirmed live 2026-08-10 — so callers must branch on which appeared.
export async function startStandaloneSubscribe(page) {
  await page.getByRole('button', { name: 'Subscribe & Save' }).click();
}

// Completes the 1 AED card-verification payment once its screen is showing
// (Checkout.com only in this flow; submit button is "Subscribe with Card",
// not "Subscribe Now" as SKILL.md says — UI has evolved) -> 3DS if it
// appears -> "Welcome to" trial screen (confirmed live: 30-day trial, not
// the "7 days" SKILL.md prose states) -> "Pay the Bill" returns to the
// Landing Page.
async function fillStandaloneCardAndSubmit(page, card = CARD) {
  const checkoutFrame = page.locator('[data-testid="card-number"]');
  await checkoutFrame.waitFor({ state: 'visible', timeout: 45000 });
  await checkoutFrame.contentFrame().getByTestId('card-number').fill(card.number);
  await page.locator('[data-testid="card-expiry-date"]').contentFrame().getByTestId('card-expiry-date').fill(card.expiry);
  await page.locator('[data-testid="card-cvv"]').contentFrame().getByTestId('card-cvv').fill(card.cvv);
  await page.getByRole('button', { name: 'Subscribe with Card' }).click();
}

export async function completeStandaloneCardPayment(page, { password = 'Checkout1!', card = CARD } = {}) {
  await fillStandaloneCardAndSubmit(page, card);

  const dialogFrame = page.locator('iframe[title="Embedded 3D Secure 2 Authentication"]');
  const need3ds = await dialogFrame.waitFor({ state: 'visible', timeout: 8000 }).then(() => true).catch(() => false);
  if (need3ds) {
    const threeDsFrame = dialogFrame.contentFrame().locator('iframe[name="cko-3ds2-iframe"]').contentFrame();
    await threeDsFrame.getByRole('textbox', { name: `Hint: ${password}` }).fill(password);
    await threeDsFrame.getByRole('button', { name: 'Continue' }).click();
  }

  await page.getByText('Welcome to').waitFor({ state: 'visible', timeout: 45000 });
  await page.getByRole('button', { name: 'Pay the Bill' }).click();
}

// ---------------------------------------------------------------------------
// submitStandaloneWrongPasswordUntilFailure
// Same 3-wrong-attempts-then-fail mechanic as submitWrongPasswordUntilFailure
// (confirmed live 2026-08-10: identical "N attempt(s) remaining" text inside
// the same nested 3DS iframes), but this is the Standalone 1 AED
// card-verification payment, which lives under /subscription/checkout, not
// /invoice/... — the final state is the "Card Verification Failed!" screen,
// not an invoice outcome URL. Call this AFTER fillStandaloneCardAndSubmit's
// "Subscribe with Card" click (assumes the 3DS dialog is already open) —
// use subscribeStandaloneWithWrongPassword below to do both in one call.
// ---------------------------------------------------------------------------
export async function submitStandaloneWrongPasswordUntilFailure(page, { attempts = 3 } = {}) {
  const dialogFrame = page.locator('iframe[title="Embedded 3D Secure 2 Authentication"]');
  await dialogFrame.waitFor({ state: 'visible', timeout: 15000 });

  for (let i = 1; i <= attempts; i++) {
    const threeDsFrame = dialogFrame.contentFrame().locator('iframe[name="cko-3ds2-iframe"]').contentFrame();
    await threeDsFrame.getByRole('textbox', { name: 'Hint: Checkout1!' }).fill(`WrongPass${i}`);
    await threeDsFrame.getByRole('button', { name: 'Continue' }).click();

    const remaining = attempts - i;
    if (remaining > 0) {
      await dialogFrame
        .contentFrame()
        .locator('iframe[name="cko-3ds2-iframe"]')
        .contentFrame()
        .getByText(`${remaining} attempt(s) remaining`)
        .waitFor({ state: 'visible', timeout: 10000 });
    }
  }

  await page.getByText('Card Verification Failed!').waitFor({ state: 'visible', timeout: 30000 });
}

export async function subscribeStandaloneWithWrongPassword(page, phoneSuffix, { card = CARD, attempts = 3 } = {}) {
  await openStandaloneSubscriptionPage(page);
  await startStandaloneSubscribe(page);
  await fillPhoneAndRequestOtp(page, phoneSuffix);
  await fillOtpAndSubmit(page, 'Subscribe');
  await fillStandaloneCardAndSubmit(page, card);
  await submitStandaloneWrongPasswordUntilFailure(page, { attempts });
}

// ---------------------------------------------------------------------------
// subscribeStandalone
// Full new-user Standalone subscription flow, composed from the pieces
// above: banner -> intro page -> phone/OTP (its own dialog, distinct from
// both the Subscription Checkbox's and "Login to qlub"'s — submits via
// "Receive Code" then "Subscribe") -> 1 AED card-verification payment.
// ---------------------------------------------------------------------------
export async function subscribeStandalone(page, phoneSuffix, opts = {}) {
  await openStandaloneSubscriptionPage(page);
  await startStandaloneSubscribe(page);
  await fillPhoneAndRequestOtp(page, phoneSuffix);
  await fillOtpAndSubmit(page, 'Subscribe');
  await completeStandaloneCardPayment(page, opts);
}

// ---------------------------------------------------------------------------
// cancelSubscription
// Manage Subscription -> Cancel subscription -> pick a reason -> the
// mandatory follow-up comment box (confirmed live: checking the reason
// checkbox alone does NOT enable "Confirm cancellation" — the follow-up
// text field must have content too) -> confirm -> the early-cancellation
// charge dialog (only shown if cancelling before the first billing date) ->
// final confirm.
//
// The early-cancellation charge dialog is NOT universal — confirmed live
// 2026-08-10: a Standalone subscriber with `restrict_early_cancel: true`
// went straight from "Confirm cancellation" to the success toast, skipping
// the "Yes, cancel my subscription" dialog entirely (General-type
// subscribers in Scenario 1/10 do see it). Race both outcomes instead of
// assuming the dialog always appears.
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// watchProfileDiscountCount
// Reads `profile.totalDiscountsUsedInCurrentPeriod` off the auth/profile API
// (`.../auth/profile?version=3&type=qlub`, confirmed live 2026-08-10) so the
// cap-limit count can be checked non-blockingly across several payments in
// one session. The updated count is NOT present on the response fired
// during/right after payment — a FOLLOW-UP profile refetch on the
// confirmation page carries the incremented value a few seconds later
// (confirmed live: the response right after landing on the outcome URL
// still read 0; waiting ~5s on the confirmation page then produced 1).
// Attach once per test (before the first payment) and keep reading `.get()`
// after each subsequent payment — no need to re-attach per table.
// ---------------------------------------------------------------------------
export function watchProfileDiscountCount(page) {
  let latest = null;
  const listener = async (res) => {
    if (!res.url().includes('/auth/profile')) return;
    const body = await res.json().catch(() => null);
    const count = body?.profile?.totalDiscountsUsedInCurrentPeriod;
    if (count !== undefined) latest = count;
  };
  page.on('response', listener);
  return {
    get: () => latest,
    stop: () => page.off('response', listener),
  };
}
export async function cancelSubscription(page, { reason = "I don't see the value for money", comment = 'I dont want anymore' } = {}) {
  await openBurgerMenu(page);
  await page.getByRole('link', { name: /Manage subscription/i }).click();
  await page.getByRole('button', { name: 'Cancel subscription' }).click();

  await page.getByRole('option', { name: reason }).getByRole('checkbox').click();
  await page.getByRole('textbox').fill(comment);
  await page.getByRole('button', { name: 'Confirm cancellation' }).click();

  const successToast = page.getByText('Subscription is successfully cancelled');
  const chargeConfirmBtn = page.getByRole('button', { name: 'Yes, cancel my subscription' });
  const chargeDialogShown = await Promise.race([
    chargeConfirmBtn.waitFor({ state: 'visible', timeout: 15000 }).then(() => true),
    successToast.waitFor({ state: 'visible', timeout: 15000 }).then(() => false),
  ]).catch(() => false);
  if (chargeDialogShown) await chargeConfirmBtn.click();

  await successToast.waitFor({ state: 'visible', timeout: 15000 });
  await page.getByRole('button', { name: 'OK' }).click();
}
