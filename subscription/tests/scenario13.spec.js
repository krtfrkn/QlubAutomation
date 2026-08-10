import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  loginViaLoginButton,
  payAndAwaitOutcome,
  getQlubPlusDiscountText,
  getLabeledAmountText,
  watchProfileDiscountCount,
} from './helpers.js';
import { getCapLimitTableUrl } from './tables.js';

// Rotated from 507391824 to the third number in SKILL.md's General-subscriber
// pool — 507391824 was hitting the documented 4-requests/hour OTP rate limit
// again after heavy reuse across today's scenario conversions (2/3/4/6/7/8/9
// plus this scenario's own live exploration), which stalled the login
// dialog on the phone step indefinitely.
const EXISTING_USER_PHONE_SUFFIX = '589012347';

test.describe('Scenario 13 - Cap Limit: General Discount Usage Cap (3 per Week)', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getCapLimitTableUrl(1));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('discount applies on 3 tables, then is blocked on a 4th once the weekly cap is reached', async ({ page }) => {
    const profile = watchProfileDiscountCount(page);

    await test.step('CL Table 1: log in and pay with discount (count -> 1)', async () => {
      await page.goto(getCapLimitTableUrl(1));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      const payableAmount = parseFloat(await getLabeledAmountText(page, 'Payable amount'));
      await loginViaLoginButton(page, EXISTING_USER_PHONE_SUFFIX);

      const expectedDiscount = `-${(payableAmount * 0.05).toFixed(2)}`;
      await expect.poll(() => getQlubPlusDiscountText(page)).toBe(expectedDiscount);
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible();

      await payAndAwaitOutcome(page);
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText("You've saved").first()).toBeVisible();

      await page.waitForTimeout(5000); // let the confirmation page's own profile refetch land
      expect.soft(profile.get()).toBe(1);
    });

    await test.step('CL Table 2: still logged in, discount pre-applied (count -> 2)', async () => {
      await page.goto(getCapLimitTableUrl(2));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible();

      await payAndAwaitOutcome(page);
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();

      await page.waitForTimeout(5000);
      expect.soft(profile.get()).toBe(2);
    });

    await test.step('CL Table 3: still logged in, discount pre-applied (count -> 3, cap reached)', async () => {
      await page.goto(getCapLimitTableUrl(3));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      await expect(page.getByText('qlub plus discount')).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible();

      await payAndAwaitOutcome(page);
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();

      await page.waitForTimeout(5000);
      expect.soft(profile.get()).toBe(3);
    });

    await test.step('CL Table 4: Weekly eligible limit banner on Landing Page', async () => {
      await page.goto(getCapLimitTableUrl(4));
      await expect(page.getByText('Weekly eligible limit reached')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText("You've used all eligible discounts for this week")).toBeVisible();
    });

    let fullPayableAmount;
    await test.step('CL Table 4: Billing Page shows no discount', async () => {
      await page.locator('[data-qa-id="landing-pay-now"]').click();
      fullPayableAmount = await getLabeledAmountText(page, 'Payable amount');
      await expect(page.getByText('You save')).toHaveCount(0);
      await expect(page.getByText('qlub plus discount')).toHaveCount(0);
    });

    await test.step('CL Table 4: pay full amount, no savings shown', async () => {
      await payAndAwaitOutcome(page);
      await expect(page.getByText('Payment was successful')).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Fully paid')).toBeVisible();
      await expect(page.getByText('You paid')).toBeVisible();
      await expect(page.getByText(fullPayableAmount, { exact: false })).toBeVisible();
      await expect(page.getByText("You've saved")).toHaveCount(0);

      await page.waitForTimeout(5000);
      expect.soft(profile.get()).toBe(3);
    });

    profile.stop();
  });
});
