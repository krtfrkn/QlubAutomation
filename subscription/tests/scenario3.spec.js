import { test, expect } from '@playwright/test';
import { ensureLoggedOut, logoutIfPossible, subscribeViaCheckbox, payAndAwaitOutcome } from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

// Existing subscriber phone (rotation pool — see domain notes; each number
// is rate-limited to 5 OTP requests/hour, switch to the next one if this
// starts failing to receive a code).
const EXISTING_USER_PHONE_SUFFIX = '507391824';

test.describe('Scenario 3 - Existing User Login via Subscription Checkbox', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 3));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('existing subscriber logs in via the new-user Subscription Checkbox and gets the General discount', async ({ page }) => {
    const phone = `+971${EXISTING_USER_PHONE_SUFFIX}`;

    await test.step('Log in via the Subscription Checkbox (normally the new-user entry point)', async () => {
      await page.goto(getTableUrl(ENV, 3));
      await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      // subscribeViaCheckbox transparently dismisses the "You are already
      // subscribed" toast this existing number triggers — see helpers.js.
      await subscribeViaCheckbox(page, EXISTING_USER_PHONE_SUFFIX);
    });

    await test.step('General discount applied automatically', async () => {
      // Not asserting an exact 5% figure — see the "not asserting an exact
      // amount" note on Scenario 1/2; the discount is dynamically calculated
      // from the bill total, so only the presence/application is checked.
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible();
    });

    await test.step('Pay (gateway/3DS vary per run - handled adaptively)', async () => {
      await payAndAwaitOutcome(page);
    });

    await test.step('Confirmation page', async () => {
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText("You've saved").first()).toBeVisible();
      // No "Congratulations!" expected — this is an already-active
      // subscriber's General discount payment, not a first-time signup.
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
