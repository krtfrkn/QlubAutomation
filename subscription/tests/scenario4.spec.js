import { test, expect } from '@playwright/test';
import { ensureLoggedOut, logoutIfPossible, loginViaLoginButton, payAndAwaitOutcome } from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';
const EXISTING_USER_PHONE_SUFFIX = '507391824';

test.describe('Scenario 4 - Existing User Login via Login Button', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 4));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('existing subscriber logs in via the dedicated Login now button and gets the General discount', async ({ page }) => {
    const phone = `+971${EXISTING_USER_PHONE_SUFFIX}`;

    await test.step('Navigate to Billing Page', async () => {
      await page.goto(getTableUrl(ENV, 4));
      await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
      await page.locator('[data-qa-id="landing-pay-now"]').click();
    });

    await test.step('Log in via the dedicated "Login now" button', async () => {
      // No toast expected on this entry point (unlike the Subscription
      // Checkbox path) — see loginViaLoginButton in helpers.js.
      await loginViaLoginButton(page, EXISTING_USER_PHONE_SUFFIX);
    });

    await test.step('General discount applied automatically', async () => {
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
