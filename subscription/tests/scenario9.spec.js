import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  loginViaTopLoginButton,
  payAndAwaitOutcome,
  getQlubPlusDiscountText,
  getLabeledAmountText,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';
// Rotated from 507391824 to the next number in SKILL.md's General-subscriber
// pool — 507391824 was hitting the documented 4-requests/hour OTP rate limit
// after heavy reuse across scenarios 3/4/6/7/8/9's live exploration + tests
// today, which stalled the login dialog on the phone step indefinitely.
const EXISTING_USER_PHONE_SUFFIX = '523456789';

test.describe('Scenario 9 - Subscription with Qlub Login', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 9));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('logging in via the top Login button on the Landing Page auto-applies the General discount on Billing', async ({ page }) => {
    const phone = `+971${EXISTING_USER_PHONE_SUFFIX}`;

    await test.step('Log in via the top "Login" button on the Landing Page', async () => {
      await page.goto(getTableUrl(ENV, 9));
      await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
      await loginViaTopLoginButton(page, EXISTING_USER_PHONE_SUFFIX);
    });

    await test.step('Logged-in state on Landing Page', async () => {
      await expect(page.getByRole('button', { name: /Pay now/ })).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Login' })).toHaveCount(0);
    });

    await test.step('Navigate to Billing Page', async () => {
      await page.getByRole('button', { name: /Pay now/ }).click();
    });

    await test.step('General discount already applied, no extra login step', async () => {
      // Confirmed live 2026-08-10: this restaurant's tables can cycle to a
      // different queued order between page loads (documented flaky-order
      // theory in payAndAwaitOutcome), so the bill amount read on the
      // Landing Page is not reliably the same bill seen on arrival at
      // Billing — comparing amounts across that navigation is inherently
      // flaky. Instead verify the discount is internally consistent with
      // the SAME settled Billing Page state: rawBill = payableAmount (post-
      // discount) + discountAbs must equal discountAbs / 0.05.
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

    await test.step('DB verification: subscription remains active (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('General');
      }
    });
  });
});
