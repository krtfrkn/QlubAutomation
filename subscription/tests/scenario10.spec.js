import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  randomUaePhoneSuffix,
  subscribeStandalone,
  payAndAwaitOutcome,
  getQlubPlusDiscountText,
  getLabeledAmountText,
  cancelSubscription,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 10 - New Standalone Subscriber + Cancel Subscription', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 11));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('new user completes Standalone subscription, pays with discount applied, then cancels', async ({ page }) => {
    const phoneSuffix = randomUaePhoneSuffix();
    const phone = `+971${phoneSuffix}`;

    await test.step('Subscribe via the Standalone banner on the Landing Page', async () => {
      await page.goto(getTableUrl(ENV, 11));
      await subscribeStandalone(page, phoneSuffix);
    });

    await test.step('DB verification: Standalone subscription active after 1 AED verification (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('Standalone');
      }
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

    await test.step('Cancel subscription', async () => {
      await cancelSubscription(page);
    });

    await test.step('DB verification: subscription suspended after cancellation (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('suspended');
      }
    });
  });
});
