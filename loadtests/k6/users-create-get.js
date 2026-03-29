import http from 'k6/http'
import { check, sleep } from 'k6'

const BASE_URL = __ENV.BASE_URL || 'http://task-manager-app-service.task-manager.svc.cluster.local:8000'

export const options = {
  scenarios: {
    create_users: {
      exec: 'createUserScenario',
      executor: 'constant-arrival-rate',
      rate: 5,
      timeUnit: '1s',
      duration: '2m',
      preAllocatedVUs: 10,
      maxVUs: 30,
      tags: {
        scenario: 'create_users',
      },
    },
    get_users: {
      exec: 'getUsersScenario',
      executor: 'constant-vus',
      vus: 10,
      duration: '2m',
      tags: {
        scenario: 'get_users',
      },
    },
  },
  thresholds: {
    http_req_failed: ['rate<0.05'],
    http_req_duration: ['p(95)<1200'],
    'http_req_duration{scenario:create_users}': ['p(95)<1500'],
    'http_req_duration{scenario:get_users}': ['p(95)<800'],
    checks: ['rate>0.95'],
  },
}

function randomSuffix() {
  return `${Date.now()}-${__VU}-${__ITER}-${Math.random().toString(16).slice(2, 8)}`
}

export function createUserScenario() {
  const suffix = randomSuffix()
  const payload = JSON.stringify({
    username: `k6_user_${suffix}`,
    email: `k6_${suffix}@example.com`,
    password: 'k6_password_123',
  })

  const res = http.post(`${BASE_URL}/users`, payload, {
    headers: { 'Content-Type': 'application/json' },
    tags: { endpoint: 'POST /users' },
  })

  check(res, {
    'create user status is 201': (r) => r.status === 201,
    'create user has id': (r) => {
      if (r.status !== 201) return false
      const body = r.json()
      return body && body.id
    },
  })

  sleep(0.2)
}

export function getUsersScenario() {
  const res = http.get(`${BASE_URL}/users?offset=0&limit=50`, {
    tags: { endpoint: 'GET /users' },
  })

  check(res, {
    'get users status is 200': (r) => r.status === 200,
    'get users contains users array': (r) => {
      if (r.status !== 200) return false
      const body = r.json()
      return body && Array.isArray(body.users)
    },
  })

  sleep(0.2)
}
