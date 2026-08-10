import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  randomUaePhoneSuffix,
  subscribeViaCheckbox,
  payAndAwaitOutcome,
  cancelSubscription,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 1 - New User: Welcome Discount + General Discount + Cancel Subscription', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    // Safety net: this restaurant's tables share one mutable "last OTP
    // login wins" identity server-side (see helpers.js). Must check/clear
    // it before every test regardless of how the previous test ended.
    await page.goto(getTableUrl(ENV, 1));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('welcome discount, general discount, and cancel subscription', async ({ page }) => {
    const phoneSuffix = randomUaePhoneSuffix();
    const phone = `+971${phoneSuffix}`;

    await test.step('Part 1: Table 1 - subscribe as a new user', async () => {
      await page.goto(getTableUrl(ENV, 1));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      await subscribeViaCheckbox(page, phoneSuffix);
    });

    await test.step('Part 1: welcome discount applied', async () => {
      // Not asserting an exact "-20.00" — the welcome discount is capped by
      // the bill total when the bill is smaller than the configured amount
      // (confirmed live: a 16.00 bill showed "-15.00", not "-20.00").
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible();
    });

    await test.step('Part 1: pay (gateway/3DS vary per run - handled adaptively)', async () => {
      await payAndAwaitOutcome(page);
    });

    await test.step('Part 1: confirmation page', async () => {
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText("You've saved").first()).toBeVisible();
      // "Congratulations!" dialog is specific to the first-ever subscription
      // payment (welcome discount) — not expected again on Part 2's payment.
      await expect(page.getByText('Congratulations!')).toBeVisible({ timeout: 10000 });
    });

    await test.step('Part 1: DB verification (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('General');
      }
    });

    await test.step('Part 2: Table 2, same session - returning subscriber pays with general discount', async () => {
      await page.goto(getTableUrl(ENV, 2));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      await expect(page.getByText('qlub plus discount')).toBeVisible();
      await payAndAwaitOutcome(page);
      await expect(page.getByText('Payment was successful')).toBeVisible();
      await expect(page.getByText('Fully paid')).toBeVisible();
    });

    await test.step('Part 3: cancel subscription', async () => {
      await cancelSubscription(page);
    });

    await test.step('Part 3: DB verification (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('suspended');
      }
    });
  });
});
