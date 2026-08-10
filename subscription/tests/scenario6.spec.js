import { test, expect } from '@playwright/test';
import { ensureLoggedOut, logoutIfPossible, loginViaLoginButton } from './helpers.js';
import { getTableUrl } from './tables.js';

const ENV = process.env.TEST_ENV || 'stg';
const EXISTING_USER_PHONE_SUFFIX = '507391824';

test.describe('Scenario 6 - No Split After Login', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 6));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('Split bill button is hidden after logging in via the dedicated Login now button, restored after logout', async ({ page }) => {
    await test.step('Navigate to Billing Page', async () => {
      await page.goto(getTableUrl(ENV, 6));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
    });

    await test.step('Split bill button present before login', async () => {
      await expect(page.getByRole('button', { name: 'Split bill' })).toBeVisible();
    });

    await test.step('Log in via the dedicated "Login now" button', async () => {
      await loginViaLoginButton(page, EXISTING_USER_PHONE_SUFFIX);
    });

    await test.step('Split bill button gone after login', async () => {
      await expect(page.getByRole('button', { name: 'Pay full bill' })).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Split bill' })).toHaveCount(0);
    });

    await test.step('Log out via Burger Menu', async () => {
      await ensureLoggedOut(page);
    });

    await test.step('Navigate back to Billing Page', async () => {
      await expect(page.getByRole('button', { name: 'Login' })).toBeVisible();
      await page.locator('[data-qa-id="landing-pay-now"]').click();
    });

    await test.step('Split bill button restored after logout', async () => {
      await expect(page.getByRole('button', { name: 'Split bill' })).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Login now' })).toBeVisible();
    });
  });
});
