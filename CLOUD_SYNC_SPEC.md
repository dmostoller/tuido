# Tuido Cloud Sync Service - Technical Specification

**Version**: 1.0
**Last Updated**: 2025-10-20
**Domain**: tuido.vercel.app

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Database Schema](#database-schema)
5. [API Endpoints](#api-endpoints)
6. [Authentication Flow](#authentication-flow)
7. [Blob Storage](#blob-storage)
8. [Security Considerations](#security-considerations)
9. [Environment Variables](#environment-variables)
10. [File Structure](#file-structure)
11. [Deployment](#deployment)
12. [Testing](#testing)

---

## Overview

Tuido Cloud Sync is a minimal web service that provides cloud backup and synchronization for the Tuido terminal application. Users authenticate via Google OAuth, receive an API token, and use the terminal app to sync their todo data to the cloud.

### Key Features

- **Authentication**: Google OAuth via NextAuth
- **Token Management**: Generate and manage API tokens for terminal app
- **Data Sync**: Upload/download user data as JSON blobs
- **Minimal UI**: Simple dashboard showing token and sync status

### Design Principles

1. **Offline-first**: Terminal app works 100% offline; cloud is optional backup
2. **Simplicity**: No real-time sync, just periodic backup/restore
3. **Privacy**: Data stored as encrypted blobs, minimal metadata
4. **Free tier**: No usage limits for MVP

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Terminal App (Python/Textual)                              │
│  - Stores data locally as JSON                              │
│  - Syncs periodically via API token                         │
│                                                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ HTTPS (API Token in header)
                         │
┌────────────────────────▼────────────────────────────────────┐
│                                                             │
│  Next.js Web App (tuido.vercel.app)                        │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Landing   │  │  Dashboard  │  │     API     │        │
│  │    Page     │  │  (Protected)│  │  Endpoints  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└────────┬────────────────────────────────────┬──────────────┘
         │                                    │
         │                                    │
┌────────▼─────────┐              ┌───────────▼──────────┐
│                  │              │                      │
│   Vercel KV      │              │   Vercel Blob        │
│   (Redis)        │              │   Storage            │
│                  │              │                      │
│  user → token    │              │  users/{id}/data.json│
│  mapping         │              │                      │
│                  │              │                      │
└──────────────────┘              └──────────────────────┘
```

### Data Flow

**Initial Setup:**
1. User visits tuido.vercel.app
2. Clicks "Sign in with Google"
3. Completes OAuth flow
4. Dashboard shows API token (UUID)
5. User copies token to terminal app

**Sync Upload (Terminal → Cloud):**
1. Terminal app sends `POST /api/sync/upload` with token + JSON data
2. API validates token → gets userId
3. Uploads data to Blob Storage at `users/{userId}/data.json`
4. Returns success + timestamp

**Sync Download (Cloud → Terminal):**
1. Terminal app sends `GET /api/sync/download` with token
2. API validates token → gets userId
3. Fetches data from Blob Storage
4. Returns JSON data + timestamp

---

## Tech Stack

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui (optional, or build custom)

### Backend
- **Runtime**: Node.js (Vercel Serverless Functions)
- **Authentication**: NextAuth.js v5 (Auth.js)
- **Database**: Vercel KV (Redis)
- **Blob Storage**: Vercel Blob Storage

### Development
- **Package Manager**: pnpm (or npm/yarn)
- **Linting**: ESLint + Prettier
- **Type Checking**: TypeScript strict mode

---

## Database Schema

### Vercel KV (Redis)

**Key-Value Store for Token Management:**

```typescript
// Key: `user:{userId}`
// Value: User object
interface User {
  id: string;           // Google user ID
  email: string;        // user@example.com
  name: string;         // Display name
  apiToken: string;     // UUID for terminal app
  createdAt: string;    // ISO-8601 timestamp
  lastSync: string;     // ISO-8601 timestamp of last sync
}

// Key: `token:{apiToken}`
// Value: userId (for fast token → user lookup)
// Example: token:550e8400-e29b-41d4-a716-446655440000 → "google-oauth2|123456"
```

**Redis Operations:**

```typescript
import { kv } from '@vercel/kv';

// Create user and token
await kv.set(`user:${userId}`, userData);
await kv.set(`token:${apiToken}`, userId);

// Lookup user by token
const userId = await kv.get(`token:${apiToken}`);
const user = await kv.get(`user:${userId}`);

// Update last sync time
await kv.set(`user:${userId}`, { ...user, lastSync: new Date().toISOString() });
```

---

## API Endpoints

### Base URL
```
https://tuido.vercel.app/api
```

### Authentication
All API endpoints require an API token in the `Authorization` header:

```http
Authorization: Bearer {apiToken}
```

---

### `POST /api/sync/upload`

Upload user data to cloud.

**Request:**
```http
POST /api/sync/upload HTTP/1.1
Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "timestamp": "2025-10-20T01:30:00.000Z",
  "projects": [
    {
      "id": "uuid",
      "name": "Personal",
      "created_at": "2025-01-01T00:00:00.000Z"
    }
  ],
  "tasks": {
    "project-uuid": [
      {
        "id": "task-uuid",
        "title": "Buy groceries",
        "completed": false,
        "created_at": "2025-01-01T00:00:00.000Z"
      }
    ]
  },
  "notes": [
    {
      "id": "note-uuid",
      "title": "Meeting notes",
      "content": "# Notes\n\nContent here",
      "created_at": "2025-01-01T00:00:00.000Z"
    }
  ]
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "timestamp": "2025-10-20T01:30:00.000Z",
  "dataSize": 1024
}
```

**Response (401 Unauthorized):**
```json
{
  "error": "Invalid or missing API token"
}
```

**Response (413 Payload Too Large):**
```json
{
  "error": "Data size exceeds 10MB limit"
}
```

---

### `GET /api/sync/download`

Download latest user data from cloud.

**Request:**
```http
GET /api/sync/download HTTP/1.1
Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "timestamp": "2025-10-20T01:30:00.000Z",
  "projects": [...],
  "tasks": {...},
  "notes": [...]
}
```

**Response (404 Not Found):**
```json
{
  "error": "No cloud data found for this user"
}
```

---

### `GET /api/sync/check`

Get timestamp of last cloud sync (lightweight check).

**Request:**
```http
GET /api/sync/check HTTP/1.1
Authorization: Bearer 550e8400-e29b-41d4-a716-446655440000
```

**Response (200 OK):**
```json
{
  "lastSync": "2025-10-20T01:30:00.000Z",
  "dataSize": 1024
}
```

---

### `POST /api/token/regenerate`

Regenerate API token (requires web session).

**Request:**
```http
POST /api/token/regenerate HTTP/1.1
Cookie: next-auth.session-token=...
```

**Response (200 OK):**
```json
{
  "apiToken": "new-uuid-token",
  "message": "Token regenerated. Update your terminal app with the new token."
}
```

---

## Authentication Flow

### Google OAuth Setup

1. **Create Google OAuth credentials:**
   - Go to Google Cloud Console
   - Create new OAuth 2.0 Client ID
   - Add authorized redirect: `https://tuido.vercel.app/api/auth/callback/google`

2. **NextAuth Configuration:**

```typescript
// app/api/auth/[...nextauth]/route.ts
import NextAuth from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { kv } from "@vercel/kv";
import { randomUUID } from "crypto";

const handler = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user, account }) {
      if (!user.email) return false;

      // Check if user exists
      const existingUser = await kv.get(`user:${user.id}`);

      if (!existingUser) {
        // Create new user and generate API token
        const apiToken = randomUUID();
        const userData = {
          id: user.id,
          email: user.email,
          name: user.name || "",
          apiToken,
          createdAt: new Date().toISOString(),
          lastSync: null,
        };

        await kv.set(`user:${user.id}`, userData);
        await kv.set(`token:${apiToken}`, user.id);
      }

      return true;
    },
    async session({ session, token }) {
      if (token.sub) {
        const user = await kv.get(`user:${token.sub}`);
        session.user = user;
      }
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
});

export { handler as GET, handler as POST };
```

### User Flow

1. **First-time user:**
   - Visits tuido.vercel.app
   - Clicks "Sign in with Google"
   - Completes OAuth consent
   - Redirected to dashboard
   - Sees API token with copy button

2. **Returning user:**
   - Visits tuido.vercel.app
   - Clicks "Sign in with Google"
   - Immediately redirected to dashboard
   - Sees existing API token

---

## Blob Storage

### Storage Structure

```
blobs/
└── users/
    ├── {userId}/
    │   └── data.json  (always overwrites)
```

### Implementation

```typescript
// lib/blob.ts
import { put, head, del } from '@vercel/blob';

export async function uploadUserData(userId: string, data: any): Promise<string> {
  const blob = await put(`users/${userId}/data.json`, JSON.stringify(data), {
    access: 'public',
    addRandomSuffix: false, // Always overwrite same file
  });

  return blob.url;
}

export async function downloadUserData(userId: string): Promise<any> {
  try {
    const response = await fetch(`https://blob.vercel-storage.com/users/${userId}/data.json`);
    if (!response.ok) return null;
    return await response.json();
  } catch {
    return null;
  }
}

export async function getUserDataSize(userId: string): Promise<number> {
  try {
    const metadata = await head(`users/${userId}/data.json`);
    return metadata.size;
  } catch {
    return 0;
  }
}
```

### API Implementation Example

```typescript
// app/api/sync/upload/route.ts
import { put } from '@vercel/blob';
import { kv } from '@vercel/kv';
import { NextRequest, NextResponse } from 'next/server';

export async function POST(req: NextRequest) {
  // Extract token from Authorization header
  const authHeader = req.headers.get('authorization');
  const token = authHeader?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Missing API token' }, { status: 401 });
  }

  // Lookup user by token
  const userId = await kv.get(`token:${token}`);
  if (!userId) {
    return NextResponse.json({ error: 'Invalid API token' }, { status: 401 });
  }

  // Parse request body
  const data = await req.json();

  // Validate data size (10MB limit)
  const dataSize = JSON.stringify(data).length;
  if (dataSize > 10 * 1024 * 1024) {
    return NextResponse.json({ error: 'Data exceeds 10MB limit' }, { status: 413 });
  }

  // Upload to blob storage
  const blob = await put(`users/${userId}/data.json`, JSON.stringify(data), {
    access: 'public',
    addRandomSuffix: false,
  });

  // Update last sync time
  const user = await kv.get(`user:${userId}`);
  await kv.set(`user:${userId}`, {
    ...user,
    lastSync: data.timestamp,
  });

  return NextResponse.json({
    success: true,
    timestamp: data.timestamp,
    dataSize,
  });
}
```

---

## Security Considerations

### API Token Security

1. **Token Generation**:
   - Use `crypto.randomUUID()` for unpredictable tokens
   - Store securely in Vercel KV
   - Never expose in client-side code

2. **Token Validation**:
   - Validate on every API request
   - Use Redis for fast lookup
   - Rate limit token usage (future enhancement)

3. **Token Regeneration**:
   - Allow users to regenerate tokens
   - Invalidate old token immediately
   - Show warning that terminal app will need update

### Data Security

1. **Transport Security**:
   - All API calls over HTTPS
   - No sensitive data in URLs (use request body)

2. **Storage Security**:
   - Blob storage access controlled by Vercel
   - No public listing of user directories
   - Optional: Add client-side encryption (future)

3. **OAuth Security**:
   - Use NextAuth built-in CSRF protection
   - Validate OAuth state parameter
   - Short-lived session tokens

### CORS Configuration

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(req: NextRequest) {
  const res = NextResponse.next();

  // Allow terminal app to call API
  if (req.nextUrl.pathname.startsWith('/api/sync')) {
    res.headers.set('Access-Control-Allow-Origin', '*');
    res.headers.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
    res.headers.set('Access-Control-Allow-Headers', 'Authorization, Content-Type');
  }

  return res;
}
```

---

## Environment Variables

Create a `.env.local` file:

```bash
# NextAuth
NEXTAUTH_URL=https://tuido.vercel.app
NEXTAUTH_SECRET=your-secret-key-here  # Generate with: openssl rand -base64 32

# Google OAuth
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# Vercel KV (auto-populated by Vercel)
KV_URL=
KV_REST_API_URL=
KV_REST_API_TOKEN=
KV_REST_API_READ_ONLY_TOKEN=

# Vercel Blob (auto-populated by Vercel)
BLOB_READ_WRITE_TOKEN=
```

---

## File Structure

```
tuido-cloud-sync/
├── app/
│   ├── api/
│   │   ├── auth/
│   │   │   └── [...nextauth]/
│   │   │       └── route.ts         # NextAuth configuration
│   │   ├── sync/
│   │   │   ├── upload/
│   │   │   │   └── route.ts         # POST /api/sync/upload
│   │   │   ├── download/
│   │   │   │   └── route.ts         # GET /api/sync/download
│   │   │   └── check/
│   │   │       └── route.ts         # GET /api/sync/check
│   │   └── token/
│   │       └── regenerate/
│   │           └── route.ts         # POST /api/token/regenerate
│   ├── dashboard/
│   │   └── page.tsx                 # Protected dashboard page
│   ├── login/
│   │   └── page.tsx                 # Login page
│   ├── layout.tsx                   # Root layout
│   ├── page.tsx                     # Landing page
│   └── globals.css                  # Global styles
├── components/
│   ├── header.tsx                   # Site header
│   ├── token-display.tsx            # Token with copy button
│   └── sync-stats.tsx               # Last sync info
├── lib/
│   ├── auth.ts                      # Auth helpers
│   ├── blob.ts                      # Blob storage helpers
│   └── kv.ts                        # KV helpers
├── middleware.ts                    # CORS middleware
├── .env.local                       # Environment variables
├── next.config.js                   # Next.js config
├── package.json                     # Dependencies
├── tsconfig.json                    # TypeScript config
└── tailwind.config.ts               # Tailwind config
```

---

## Deployment

### Prerequisites

1. **Vercel Account**: Sign up at vercel.com
2. **Google OAuth Credentials**: From Google Cloud Console
3. **Domain** (optional): Configure tuido.vercel.app or custom domain

### Steps

1. **Create Vercel Project**:
   ```bash
   vercel login
   vercel init
   vercel link
   ```

2. **Enable Vercel KV**:
   - Go to Vercel Dashboard → Storage
   - Create new KV database
   - Environment variables auto-populated

3. **Enable Vercel Blob**:
   - Go to Vercel Dashboard → Storage
   - Enable Blob storage
   - Environment variables auto-populated

4. **Configure Environment Variables**:
   - Add `NEXTAUTH_URL`, `NEXTAUTH_SECRET`
   - Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`

5. **Deploy**:
   ```bash
   vercel --prod
   ```

6. **Configure Google OAuth**:
   - Add authorized redirect: `https://tuido.vercel.app/api/auth/callback/google`

### Monitoring

- **Vercel Dashboard**: View deployments, logs, analytics
- **Vercel KV Dashboard**: View Redis data
- **Vercel Blob Dashboard**: View storage usage

---

## Testing

### Local Development

```bash
# Install dependencies
pnpm install

# Run development server
pnpm dev

# Open http://localhost:3000
```

### Test API Endpoints

```bash
# Upload test
curl -X POST http://localhost:3000/api/sync/upload \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2025-01-01T00:00:00Z","projects":[],"tasks":{},"notes":[]}'

# Download test
curl http://localhost:3000/api/sync/download \
  -H "Authorization: Bearer test-token"

# Check test
curl http://localhost:3000/api/sync/check \
  -H "Authorization: Bearer test-token"
```

### Integration Testing

1. **Sign in flow**:
   - Visit http://localhost:3000
   - Click "Sign in with Google"
   - Verify redirect to dashboard
   - Verify token is displayed

2. **API flow**:
   - Copy token from dashboard
   - Use curl to upload test data
   - Use curl to download data
   - Verify data matches

3. **Token regeneration**:
   - Click "Regenerate Token"
   - Verify old token is invalid
   - Verify new token works

---

## Future Enhancements

### MVP+
- [ ] Sync history (last 10 syncs)
- [ ] Download data as backup JSON
- [ ] Delete account functionality
- [ ] Usage stats (sync count, data size over time)

### Premium Features
- [ ] Rate limiting (100 syncs/day free, unlimited paid)
- [ ] Larger storage limits (10MB free, 100MB paid)
- [ ] Client-side encryption
- [ ] Sync versioning/history
- [ ] Team collaboration
- [ ] API webhooks

---

## API Response Codes Summary

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful request |
| 401 | Unauthorized | Invalid/missing token |
| 404 | Not Found | No data exists for user |
| 413 | Payload Too Large | Data exceeds 10MB |
| 429 | Too Many Requests | Rate limit exceeded (future) |
| 500 | Internal Server Error | Server error |

---

## Support

For questions or issues:
- **GitHub Issues**: [github.com/yourusername/tuido-cloud-sync](https://github.com)
- **Email**: support@tuido.vercel.app

---

**End of Specification**
