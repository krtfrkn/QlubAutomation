import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  loginViaLoginButton,
  getQlubPlusDiscountText,
  getLabeledAmountText,
} from './helpers.js';
import { getTableUrl } from './tables.js';

const ENV = process.env.TEST_ENV || 'stg';
const EXISTING_USER_PHONE_SUFFIX = '507391824';

test.describe('Scenario 8 - Tip is Not Included in Discount (before login)', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 8));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('a tip selected before login stays selected after login and is excluded from the qlub+ discount', async ({ page }) => {
    let payableAmount;

    await test.step('Navigate to Billing Page', async () => {
      await page.goto(getTableUrl(ENV, 8));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      payableAmount = parseFloat(await getLabeledAmountText(page, 'Payable amount'));
    });

    await test.step('Select a tip before login', async () => {
      // Confirmed live 2026-08-09: the tip buttons don't have a stable
      // data-selected attribute, but the "Tip amount:" indicator reliably
      // reflects the active selection — simpler and more robust to assert
      // against than the tip button's own DOM/class state.
      await page.locator('#tip_10').click();
      await expect.poll(() => getLabeledAmountText(page, 'Tip amount:')).toBe('10.00');
    });

    await test.step('Log in via the dedicated "Login now" button', async () => {
      await loginViaLoginButton(page, EXISTING_USER_PHONE_SUFFIX);
    });

    await test.step('Tip is still selected after login', async () => {
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await expect.poll(() => getLabeledAmountText(page, 'Tip amount:')).toBe('10.00');
    });

    await test.step('Discount reflects pre-tip, pre-login payable amount only', async () => {
      const expectedDiscount = `-${(payableAmount * 0.05).toFixed(2)}`;
      await expect.poll(() => getQlubPlusDiscountText(page)).toBe(expectedDiscount);

      const expectedYouPay = (payableAmount - payableAmount * 0.05 + 10).toFixed(2);
      await expect.poll(() => getLabeledAmountText(page, 'You pay')).toBe(expectedYouPay);
    });
  });
});
