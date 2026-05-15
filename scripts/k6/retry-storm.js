import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  scenarios: {
    retry_storm: {
      executor: 'constant-arrival-rate',
      rate: 50,
      timeUnit: '1s',
      duration: '1m',
      preAllocatedVUs: 50,
      maxVUs: 100,
    },
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://traefik';

export default function () {
  // Simulate a client that retries aggressively on error
  let res = http.get(`${BASE_URL}/simulate/error`);
  
  let retries = 0;
  while (res.status === 500 && retries < 3) {
    retries++;
    sleep(0.1); // Short sleep before retry
    res = http.get(`${BASE_URL}/simulate/error`);
  }

  check(res, {
    'eventually succeeded or failed': (r) => r.status === 200 || r.status === 500,
  });
}
