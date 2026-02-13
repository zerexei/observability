import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 50 }, // Ramp-up to 50 users over 30 seconds
    { duration: "1m", target: 100 }, // Maintain 100 users for 1 minute
    { duration: "30s", target: 50 }, // Ramp-down to 50 users over 30 seconds
  ],
};

export default function () {
  const res = http.get("http://app:8000"); // Replace with your app URL
  check(res, {
    "is status 200": (r) => r.status === 200,
  });
  sleep(1);
}
