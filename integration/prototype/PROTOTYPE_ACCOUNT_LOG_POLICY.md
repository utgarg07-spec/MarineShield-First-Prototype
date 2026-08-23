# Prototype Account & Profile Metadata Policy

**Target System:** MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Policy Purpose:** Definition of permitted non-sensitive user metadata storage vs. strictly prohibited credential persistence.  
**Created Timestamp:** 2026-08-23 (UTC)  
**Security Status:** COMPLIANT WITH FIREBASE SECURITY AND ZERO-PLAINTEXT STORAGE RULES

---

## 1. Permitted Non-Sensitive Metadata

The prototype authentication layer manages user identity strictly via Firebase Authentication. The following non-sensitive metadata items may be held in memory or local user session state:

1. **Firebase User UID:** (`fbUser.uid`) Unique identifier assigned by Firebase.
2. **Display Name:** (`fbUser.displayName`) User's full name.
3. **Email Address:** (`fbUser.email`) Email address bound to the Firebase account.
4. **Prototype Operator ID:** (`OP-XXXX`) Client-side prototype identifier mapped to the session for command center display.
5. **Session Timestamps:** (`loginTime`, `createdAt`) Standard ISO 8601 UTC timestamps for operational auditing.

---

## 2. Strictly Prohibited Items (Never Persisted)

Under NO circumstances shall any of the following items be logged, stored, printed, exported, or written to any local or remote file, console log, report, or repository:

1. **Plaintext Passwords:** NEVER stored in React state, `localStorage`, `sessionStorage`, files, or logs.
2. **Password Hashes / Digests:** Frontend does not hash or handle password digests; authentication occurs exclusively via Firebase Web SDK.
3. **Firebase ID Tokens / Refresh Tokens:** Tokens remain managed internally by the Firebase Web SDK.
4. **Firebase Private Keys / Service Account Keys:** No service accounts or private keys exist on the client side.
5. **Sensitive Personal Identifiers:** No financial, passport, or private personal data is collected or stored.

---

## 3. Storage Scope & Disclaimer

- **Client Session Scope:** User session metadata is stored in `localStorage` under `marineshield_user_session` solely for UI state restoration across page reloads.
- **Prototype Disclaimer:** Client-side storage of Operator IDs is for prototype demonstration only and does NOT constitute server-side RBAC authorization.
