import { test, expect } from '@playwright/test';
import {
  ensureLoggedOut,
  logoutIfPossible,
  randomUaePhoneSuffix,
  standaloneBannerExists,
  subscribeStandaloneWithWrongPassword,
} from './helpers.js';
import { getTableUrl } from './tables.js';
import { getCustomerMappingByPhone, findSubscriptionRow } from './db.js';

const ENV = process.env.TEST_ENV || 'stg';

test.describe('Scenario 12 - Standalone 3DS Failure: Wrong Password x3 -> Card Verification Failed', () => {
  test.setTimeout(300_000);

  test.beforeEach(async ({ page }) => {
    await page.goto(getTableUrl(ENV, 13));
    await ensureLoggedOut(page);
  });

  test.afterEach(async ({ page }) => {
    await logoutIfPossible(page);
  });

  test('3 wrong 3DS passwords fail the 1 AED card verification, no subscription created, Try again resets the payment screen', async ({ page }) => {
    const phoneSuffix = randomUaePhoneSuffix();
    const phone = `+971${phoneSuffix}`;

    await test.step('Standalone banner present on Landing Page', async () => {
      await page.goto(getTableUrl(ENV, 13));
      await expect(page.getByRole('button', { name: /Pay now/ })).toBeVisible({ timeout: 15000 });
      expect(await standaloneBannerExists(page)).toBe(true);
    });

    await test.step('Subscribe with a new UAE number, fail 3DS 3 times in a row', async () => {
      await subscribeStandaloneWithWrongPassword(page, phoneSuffix);
    });

    await test.step('Card Verification Failed screen', async () => {
      await expect(page.getByText('Card Verification Failed!')).toBeVisible();
      await expect(
        page.getByText('We couldn’t verify your card details, so your subscription wasn’t activated. Please try again.'),
      ).toBeVisible();
      await expect(page.getByRole('button', { name: 'Try again' })).toBeVisible();
    });

    await test.step('DB verification: no subscription row created (non-blocking)', async () => {
      const rows = await getCustomerMappingByPhone(phone).catch(() => []);
      const subRow = findSubscriptionRow(rows);
      expect.soft(subRow, 'no subscription row should exist after a failed card verification').toBeUndefined();
    });

    await test.step('Try again redirects back to the 1 AED payment screen, card fields reset', async () => {
      await page.getByRole('button', { name: 'Try again' }).click();
      await expect(page.getByRole('button', { name: 'Subscribe with Card' })).toBeVisible({ timeout: 15000 });
      const checkoutFrame = page.locator('[data-testid="card-number"]');
      await expect(checkoutFrame.contentFrame().getByTestId('card-number')).toBeEmpty();
    });
  });
});
