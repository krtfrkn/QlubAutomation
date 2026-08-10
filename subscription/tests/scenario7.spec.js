import { test, expect } from '@playwright/test';
import { ensureLoggedOut, logoutIfPossible, loginViaLoginButton, getQlubPlusDiscountText } from './helpers.js';
import { getTableUrl } from './tables.js';

const ENV = process.env.TEST_ENV || 'stg';
const EXISTING_USER_PHONE_SUFFIX = '507391824';

test.describe('Scenario 7 - Tip is Not Included in Discount (after login)', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 7));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('adding a tip after login does not change the qlub+ discount amount', async ({ page }) => {
    await test.step('Navigate to Billing Page', async () => {
      await page.goto(getTableUrl(ENV, 7));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
    });

    await test.step('Log in via the dedicated "Login now" button', async () => {
      await loginViaLoginButton(page, EXISTING_USER_PHONE_SUFFIX);
    });

    let discountBeforeTip;
    await test.step('Read discount amount before tip', async () => {
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      discountBeforeTip = await getQlubPlusDiscountText(page);
    });

    await test.step('Select a tip', async () => {
      await page.getByText('10.00', { exact: true }).click();
    });

    await test.step('Discount amount unchanged after tip', async () => {
      await expect
        .poll(() => getQlubPlusDiscountText(page), { timeout: 10000 })
        .toBe(discountBeforeTip);
    });
  });
});
