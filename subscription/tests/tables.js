// QR table URLs for the `furkanSubscriptionAutomation` restaurant, per environment.
// Extend this map as later scenarios get converted — only the tables actually
// exercised by converted scenarios need to be present.
const TABLES = {
  stg: {
    baseUrl: 'https://app-staging.qlub.cloud',
    tables: {
      1: '/qr/ae/furkanSubscriptionAutomation/1/_/_/35f7042757',
      2: '/qr/ae/furkanSubscriptionAutomation/2/_/_/577429c297',
      3: '/qr/ae/furkanSubscriptionAutomation/3/_/_/fe5ae86801',
      4: '/qr/ae/furkanSubscriptionAutomation/4/_/_/89b432ecf2',
      5: '/qr/ae/furkanSubscriptionAutomation/5/_/_/4d4f041013',
      6: '/qr/ae/furkanSubscriptionAutomation/6/_/_/1097dc35ab',
      7: '/qr/ae/furkanSubscriptionAutomation/7/_/_/e402fc4578',
      8: '/qr/ae/furkanSubscriptionAutomation/8/_/_/8a6e85627b',
      9: '/qr/ae/furkanSubscriptionAutomation/9/_/_/5ebc39fdf1',
      10: '/qr/ae/furkanSubscriptionAutomation/10/_/_/1614099736',
      11: '/qr/ae/furkanSubscriptionAutomation/11/_/_/6d55f45b13',
      12: '/qr/ae/furkanSubscriptionAutomation/12/_/_/0562f7d18c',
      13: '/qr/ae/furkanSubscriptionAutomation/13/_/_/1741580c50',
    },
  },
  dev6: {
    baseUrl: 'https://app-dev6.qlub.cloud',
    tables: {
      1: '/qr/ae/furkanSubscriptionAutomation/1/_/_/6bcd0e0209',
      2: '/qr/ae/furkanSubscriptionAutomation/2/_/_/28b4eeb023',
      3: '/qr/ae/furkanSubscriptionAutomation/3/_/_/e5e81e303f',
      4: '/qr/ae/furkanSubscriptionAutomation/4/_/_/5e0fc408f7',
      5: '/qr/ae/furkanSubscriptionAutomation/5/_/_/3677e863b4',
      6: '/qr/ae/furkanSubscriptionAutomation/6/_/_/cd4247d510',
      7: '/qr/ae/furkanSubscriptionAutomation/7/_/_/2afd455727',
      8: '/qr/ae/furkanSubscriptionAutomation/8/_/_/ec192e69e0',
      9: '/qr/ae/furkanSubscriptionAutomation/9/_/_/6e13ba8128',
      10: '/qr/ae/furkanSubscriptionAutomation/10/_/_/f09aaadc1d',
      11: '/qr/ae/furkanSubscriptionAutomation/11/_/_/b9ced8f2ba',
      12: '/qr/ae/furkanSubscriptionAutomation/12/_/_/bd00290186',
      13: '/qr/ae/furkanSubscriptionAutomation/13/_/_/0225dc6bd5',
    },
  },
  dev7: {
    baseUrl: 'https://app-dev7.qlub.cloud',
    tables: {
      1: '/qr/ae/furkanSubscriptionAutomation/1/_/_/b3a8ca38ac',
      2: '/qr/ae/furkanSubscriptionAutomation/2/_/_/1c801f1d92',
      3: '/qr/ae/furkanSubscriptionAutomation/3/_/_/535bf09dc8',
      4: '/qr/ae/furkanSubscriptionAutomation/4/_/_/d7150ce236',
      5: '/qr/ae/furkanSubscriptionAutomation/5/_/_/a2eea2ada7',
      6: '/qr/ae/furkanSubscriptionAutomation/6/_/_/fdefd87d1d',
      7: '/qr/ae/furkanSubscriptionAutomation/7/_/_/4be020f7c0',
      8: '/qr/ae/furkanSubscriptionAutomation/8/_/_/9a21635749',
      9: '/qr/ae/furkanSubscriptionAutomation/9/_/_/0f4f965474',
      10: '/qr/ae/furkanSubscriptionAutomation/10/_/_/3cffd9ae87',
      11: '/qr/ae/furkanSubscriptionAutomation/11/_/_/20ab34b4f4',
      12: '/qr/ae/furkanSubscriptionAutomation/12/_/_/cd193aaa07',
      13: '/qr/ae/furkanSubscriptionAutomation/13/_/_/b92d1db193',
    },
  },
};

export function getTableUrl(env, tableNumber) {
  const envConfig = TABLES[env];
  if (!envConfig) throw new Error(`Unknown environment "${env}"`);
  const path = envConfig.tables[tableNumber];
  if (!path) throw new Error(`Table ${tableNumber} not mapped for environment "${env}"`);
  return `${envConfig.baseUrl}${path}`;
}

// The `subscriptionAutomationCapLimit` restaurant is a separate slug, dedicated
// to Scenario 13's cap-limit checks — dev6 only (per SKILL.md). Kept apart
// from TABLES above since that map is scoped to `furkanSubscriptionAutomation`.
const CAP_LIMIT_TABLES_DEV6 = {
  1: '/qr/ae/subscriptionAutomationCapLimit/1/_/_/c3aabd5650',
  2: '/qr/ae/subscriptionAutomationCapLimit/2/_/_/36dc40ce65',
  3: '/qr/ae/subscriptionAutomationCapLimit/3/_/_/73fd905fc9',
  4: '/qr/ae/subscriptionAutomationCapLimit/4/_/_/f89202f5e2',
  5: '/qr/ae/subscriptionAutomationCapLimit/5/_/_/6f465908ef',
};

export function getCapLimitTableUrl(tableNumber) {
  const path = CAP_LIMIT_TABLES_DEV6[tableNumber];
  if (!path) throw new Error(`Cap Limit table ${tableNumber} not mapped`);
  return `https://app-dev6.qlub.cloud${path}`;
}
