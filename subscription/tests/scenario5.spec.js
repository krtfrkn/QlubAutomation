import { test, expect } from '@playwright/test';
import { ensureLoggedOut, logoutIfPossible, splitBillEqually, removeSplit } from './helpers.js';
import { getTableUrl } from './tables.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 5 - No Subscription After Split', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 5));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('subscription checkbox and Login now banner are hidden while split, reappear after removing the split', async ({ page }) => {
    await test.step('Navigate to Billing Page', async () => {
      await page.goto(getTableUrl(ENV, 5));
      await page.locator('[data-qa-id="landing-pay-now"]').click();
    });

    await test.step('Subscription elements present before split', async () => {
      await expect(page.getByRole('button', { name: 'Login now' })).toBeVisible();
      await expect(page.getByText('Already a qlub+ member?')).toBeVisible();
    });

    await test.step('Split the bill equally', async () => {
      // Confirmed live 2026-08-09: each split option (in the "Split the
      // bill" sheet) is a single clickable button whose accessible name
      // combines its title + subtitle text, not a separate heading + a
      // dedicated "select" button as the prose describes — UI has evolved.
      // splitBillEqually also retries the "Confirm" click — confirmed live
      // it can intermittently fail to close the sheet on the first attempt.
      await splitBillEqually(page);
    });

    await test.step('Subscription elements hidden after split', async () => {
      await expect(page.getByRole('button', { name: 'Edit split' })).toBeVisible();
      await expect(page.getByRole('button', { name: 'Login now' })).toHaveCount(0);
      await expect(page.getByText('Already a qlub+ member?')).toHaveCount(0);
    });

    await test.step('Remove the split', async () => {
      await removeSplit(page);
    });

    await test.step('Subscription elements reappear after removing split', async () => {
      await expect(page.getByRole('button', { name: 'Split bill' })).toBeVisible({ timeout: 15000 });
      await expect(page.getByRole('button', { name: 'Login now' })).toBeVisible({ timeout: 15000 });
      await expect(page.getByText('Already a qlub+ member?')).toBeVisible({ timeout: 15000 });
    });
  });
});
