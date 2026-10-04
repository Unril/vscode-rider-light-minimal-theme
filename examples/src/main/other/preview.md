# User Service API

A lightweight REST API for managing user accounts. Built with **TypeScript** and deployed on [Node.js 22 LTS](https://nodejs.org). See the `README` for setup instructions.

## Quick Start

### Authentication

Requests are authenticated via JWT tokens signed with HS256.

#### Token Format

The payload contains `sub` (user ID), `role`, and `exp` (expiration).

##### Refresh Tokens

Refresh tokens are stored server-side and rotated on each use.

###### Rate Limits

Each client is limited to 60 requests per minute per API key.

## Code Example

```typescript
interface User {
  readonly id: string;
  name: string;
  role: "admin" | "viewer";
}

async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) {
    throw new Error(`User not found: ${id}`);
  }
  return res.json();
}
```

## Endpoints

| Method | Endpoint | Status | Description |
| --- | --- | --- | --- |
| GET | `/api/users` | 200 | List all users |
| POST | `/api/users` | 201 | Create a user |
| DELETE | `/api/users/:id` | 204 | Remove a user |

## Setup

Clone the repository and follow the steps below. The project uses `npm` for package management and expects a _PostgreSQL_ database for persistence. The ~~SQLite backend~~ has been removed in v2.

- Install dependencies
  - Runtime
    1. Node.js 22 LTS
    2. TypeScript 5.7
       - Strict mode enabled
         1. Set `strict: true` in `tsconfig.json`
            - Catches type errors
              1. At compile time
  - Dev tools
    1. ESLint for linting
    2. Prettier for formatting
- Configure the project
  - Copy `.env.example` to `.env`
    1. Set `DATABASE_URL`
    2. Set `JWT_SECRET`
       - Use a 256-bit random key
- Run the test suite
  - Unit tests with Vitest
    1. Run `npm test`
    2. Check coverage report

> The API requires authentication for all endpoints except `GET /api/users`.
> Pass a Bearer token in the `Authorization` header.
>
> > For local development, use the test token from `.env.example`.
> >
> > > In production, tokens are issued by the OAuth2 provider.
