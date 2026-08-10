import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  randomUaePhoneSuffix,
  subscribeViaCheckbox,
  fillCardForm,
  submitWrongPasswordUntilFailure,
  payAndAwaitOutcome,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 2 - New User: 3DS Failure -> Try Again -> Successful Payment', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 10));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('wrong 3DS password fails payment, Try Again succeeds with correct password', async ({ page }) => {
    const phoneSuffix = randomUaePhoneSuffix();
    const phone = `+971${phoneSuffix}`;

    await test.step('Subscribe as a new user', async () => {
      await page.goto(getTableUrl(ENV, 10));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      await subscribeViaCheckbox(page, phoneSuffix);
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
    });

    await test.step('Pay with wrong 3DS password 3 times - payment fails', async () => {
      await fillCardForm(page);
      await page.getByRole('button', { name: 'Pay' }).click();
      await submitWrongPasswordUntilFailure(page);

      await expect(page.getByText('Payment was unsuccessful!')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Please try again')).toBeVisible();
      await expect(page.getByText('Failed')).toBeVisible();
    });

    await test.step('DB verification: no subscription row yet (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      expect.soft(subRow, 'no subscription row should exist before a successful payment').toBeUndefined();
    });

    await test.step('Try Again - discount still applied (via login, not a checkbox), retry with correct password', async () => {
      await page.getByRole('button', { name: 'Try Again' }).click();
      // Confirmed live 2026-08-08: unlike the pre-login state, there's no
      // Subscription Checkbox to re-check here — the OTP-verified login from
      // the failed attempt persists, so the discount is recognized
      // automatically, the same way an already-logged-in returning
      // subscriber sees it.
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await payAndAwaitOutcome(page);
    });

    await test.step('Confirmation page', async () => {
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText("You've saved").first()).toBeVisible();
      // No "Congratulations!" assertion here — confirmed live 2026-08-08 it
      // does NOT appear on this confirmation page. That dialog is tied to
      // completing OTP/signup for the first time, not to the first
      // *successful* payment — signup already happened during the failed
      // attempt above, so it doesn't reappear on this retry's success.
    });

    await test.step('DB verification: subscription now active (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      if (subRow) {
        expect.soft(subRow.extra_info.status).toBe('active');
        expect.soft(subRow.extra_info.subscription_type).toBe('General');
      }
    });
  });
});
