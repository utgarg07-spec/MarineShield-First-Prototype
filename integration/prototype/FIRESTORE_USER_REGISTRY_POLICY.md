# Firestore User Registry Policy & Security Rules

**Target System:** MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Document Purpose:** Specification for persistent prototype user registry in Cloud Firestore (`users/{uid}`).  
**Created Timestamp:** 2026-08-23 (UTC)  
**Security Disclosure Status:** NO CREDENTIALS, SECRETS, OR TOKENS EXPOSED

---

## 1. Firestore Collection Schema (`users/{uid}`)

Each document in `users/{uid}` represents an authenticated and registered MarineShield operator profile.

| Field Name | Type | Purpose / Description | Allowed Values |
| :--- | :--- | :--- | :--- |
| `uid` | String | Firebase Authentication User Unique Identifier | Matches `request.auth.uid` |
| `normalizedEmail` | String | Lowercase, trimmed email address for lookup & auditing | e.g. `operator@marineshield.gov` |
| `displayName` | String | Operator full name | Full name string |
| `operatorId` | String | MarineShield Operator Badge/ID Number | e.g. `OP-8492` |
| `provider` | String | Authentication Provider | `'password'` \| `'google'` |
| `accountStatus` | String | Account Access Authorization Status | `'ACTIVE'` \| `'SUSPENDED'` |
| `createdAt` | Timestamp | Initial profile creation timestamp | Firestore ServerTimestamp |
| `lastLoginAt` | Timestamp | Last successful login timestamp | Firestore ServerTimestamp |
| `registryVersion` | String | Schema specification version | `'1.0-prototype'` |

---

## 2. Prohibited Fields (Never Written to Firestore)

To comply with strict security and privacy standards, the following fields are **STRICTLY PROHIBITED** from being written to Firestore or stored locally:

1. **Plaintext Passwords:** NEVER stored or transmitted outside Firebase Auth Web SDK.
2. **Password Hashes / Digests:** Client-side application does not compute or store password digests.
3. **Firebase ID Tokens & Refresh Tokens:** Managed exclusively by Firebase Web SDK internal storage.
4. **Private Keys / Service Account Keys:** No service account keys exist on the client side.

---

## 3. Account Existence & Authorization Logic

1. **Create Account Flow:**
   - User submits Create Operator Account form (Email/Password or Google).
   - Upon successful identity creation in Firebase Auth, `users/{uid}` document is written to Cloud Firestore with `accountStatus: 'ACTIVE'`.
   - Access to Command Center is granted only after the Firestore document write completes successfully.
2. **Login Flow:**
   - User authenticates via Email/Password or Google Sign-In.
   - App reads `users/{uid}` from Cloud Firestore.
   - **Rejection Policy:** If no document exists in `users/{uid}` or `accountStatus !== 'ACTIVE'`, the user is **IMMEDIATELY SIGNED OUT** from Firebase Auth, and an error message is displayed:
     > `ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE`
   - Unregistered Google accounts are blocked from accessing the Command Center until explicit registration occurs.

---

## 4. Starter Security Rules for Firebase Console

Copy these security rules into **Firebase Console -> Firestore Database -> Rules**:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

> [!IMPORTANT]
> **Prototype Limitation Notice:** This client-side registry allowlist enforces that only registered users with a valid `users/{uid}` document can enter the Command Center. For production deployment, server-side Cloud Functions or Firebase Custom Claims should be implemented for authoritative RBAC.
