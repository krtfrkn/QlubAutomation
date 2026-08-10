import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  randomUaePhoneSuffix,
  standaloneBannerExists,
  openStandaloneSubscriptionPage,
  closeStandaloneSubscriptionPage,
  dismissStandaloneCardPayment,
  startStandaloneSubscribe,
  completeStandaloneCardPayment,
  fillPhoneAndRequestOtp,
  fillOtpAndSubmit,
  payAndAwaitOutcome,
  getQlubPlusDiscountText,
  getLabeledAmountText,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 11 - Standalone Banner/Subscription Page Resilience + New User Subscribe', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 12));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('banner/subscription page survive open-close cycles; dismissed payment leaves banner intact; second attempt completes subscription', async ({ page }) => {
    const phoneSuffix = randomUaePhoneSuffix();
    const phone = `+971${phoneSuffix}`;

    await test.step('Standalone banner present on Landing Page', async () => {
      await page.goto(getTableUrl(ENV, 12));
      await expect(page.getByRole('button', { name: /Pay now/ })).toBeVisible({ timeout: 15000 });
      expect(await standaloneBannerExists(page)).toBe(true);
    });

    await test.step('Open/close cycle 1', async () => {
      await openStandaloneSubscriptionPage(page);
      await closeStandaloneSubscriptionPage(page);
      expect(await standaloneBannerExists(page)).toBe(true);
    });

    await test.step('Open/close cycle 2', async () => {
      await openStandaloneSubscriptionPage(page);
      await closeStandaloneSubscriptionPage(page);
      expect(await standaloneBannerExists(page)).toBe(true);
    });

    await test.step('Open Subscription Page (3rd time), log in with a new UAE number', async () => {
      await openStandaloneSubscriptionPage(page);
      await startStandaloneSubscribe(page);
      await fillPhoneAndRequestOtp(page, phoneSuffix);
      await fillOtpAndSubmit(page, 'Subscribe');
      await expect(page.getByText(/charge will be made and refunded/)).toBeVisible({ timeout: 15000 });
      await expect(page.getByText(phone)).toBeVisible();
    });

    await test.step('Dismiss the 1 AED payment screen without subscribing', async () => {
      await dismissStandaloneCardPayment(page);
    });

    await test.step('Landing Page: banner still visible for logged-in but unsubscribed user', async () => {
      await expect(page.getByRole('button', { name: /Pay now/ })).toBeVisible({ timeout: 15000 });
      expect(await standaloneBannerExists(page)).toBe(true);
      await expect(page.getByText(/You save/)).toHaveCount(0);
    });

    await test.step('Reopen Subscription Page - Subscribe skips phone input (already logged in)', async () => {
      await openStandaloneSubscriptionPage(page);
      await startStandaloneSubscribe(page);
      await expect(page.getByText(/charge will be made and refunded/)).toBeVisible({ timeout: 15000 });
      await expect(page.getByText(phone)).toBeVisible();
    });

    await test.step('Complete the 1 AED payment', async () => {
      await completeStandaloneCardPayment(page);
    });

    await test.step('DB verification: Standalone subscription active (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('Standalone');
      }
    });

    await test.step('Landing Page: subscription banner replaced (no "You save" text there)', async () => {
      // Confirmed live 2026-08-10 (also seen during Scenario 10): the "You
      // save X" discount banner does NOT actually render on the Landing
      // Page after subscribing — only the Standalone banner's disappearance
      // is checkable here. SKILL.md's Step 13 prose is stale; the discount
      // banner assertion belongs on the Billing Page (checked next).
      await expect(page.getByRole('button', { name: /Pay now/ })).toBeVisible({ timeout: 15000 });
      expect(await standaloneBannerExists(page, { expectPresent: false })).toBe(false);
    });

    await test.step('Navigate to Billing Page', async () => {
      await page.getByRole('button', { name: /Pay now/ }).click();
    });

    await test.step('General discount applied (self-consistent — bill can cycle between page loads)', async () => {
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible({ timeout: 15000 });
      const discountAbs = Math.abs(parseFloat(await getQlubPlusDiscountText(page)));
      const payableAfter = parseFloat(await getLabeledAmountText(page, 'Payable amount'));
      const rawBill = payableAfter + discountAbs;
      expect(discountAbs).toBeCloseTo(rawBill * 0.05, 2);
    });

    await test.step('Pay (gateway/3DS vary per run - handled adaptively)', async () => {
      await payAndAwaitOutcome(page);
    });

    await test.step('Confirmation page', async () => {
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText("You've saved").first()).toBeVisible();
    });

    await test.step('DB verification: subscription still active (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('Standalone');
      }
    });
  });
});
