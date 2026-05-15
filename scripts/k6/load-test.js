import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 }, // ramp up to 20 users
    { duration: '1m', target: 20 },  // stay at 20 users
    { duration: '30s', target: 0 },  // ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests must complete below 500ms
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://traefik';

export default function () {
  // 1. Root hit
  let res = http.get(`${BASE_URL}/`);
  check(res, { 'root status is 200': (r) => r.status === 200 });

  // 2. DB read with random latency
  res = http.get(`${BASE_URL}/items/${Math.floor(Math.random() * 100)}`);
  check(res, { 'items status is 200': (r) => r.status === 200 });

  // 3. Cache hit/miss
  res = http.get(`${BASE_URL}/cache/user_${Math.floor(Math.random() * 10)}`);
  check(res, { 'cache status is 200': (r) => r.status === 200 });

  // 4. Random failures (simulated)
  if (Math.random() < 0.1) {
    res = http.get(`${BASE_URL}/simulate/error`);
    check(res, { 'error status is 500': (r) => r.status === 500 });
  }

  // 5. Random latency (simulated)
  if (Math.random() < 0.05) {
    http.get(`${BASE_URL}/simulate/latency?ms=500`);
  }

  sleep(1);
}
