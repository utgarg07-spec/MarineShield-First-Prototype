# Persistent Prototype User Registry Report

**Task Type:** Cloud Firestore User Registry (`users/{uid}`) & Account Rejection Implementation  
**Target System:** Main MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Completion Timestamp:** 2026-08-23 (UTC)  
**Security Disclosure Status:** ZERO CREDENTIALS, SECRETS, OR TOKENS STORED OR EXPOSED  
**Final Status:** PERSISTENT PROTOTYPE REGISTRY PASSED — REGISTERED USERS ADMITTED AND UNREGISTERED USERS REJECTED

---

## 1. Executive Summary & Registry Architecture

A persistent Cloud Firestore user registry (`users/{uid}`) has been integrated into the MarineShield frontend to replace un-gated authentication. 

### Key Security & Authorization Mechanics:
1. **Create Account Flow:**
   - Submitting Create Operator Account (Email/Password or Google) creates identity in Firebase Auth and writes a non-sensitive profile document to `users/{uid}` with `accountStatus: 'ACTIVE'`.
   - Entry into Command Center is granted only after the Firestore document creation succeeds.
2. **Login Rejection for Unregistered Accounts:**
   - Authenticating via Email/Password or Google checks for the existence of `users/{uid}` in Cloud Firestore.
   - **Rejection Policy:** If no registry profile exists, the user is **IMMEDIATELY SIGNED OUT** from Firebase Auth and presented with a clear error:
     > `ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE`
   - An explicit link to open the Create Account form is offered.
3. **Operator ID Resolution:**
   - Login accepts either an Email Address or Operator ID (`OP-XXXX`). Operator IDs are queried against `users` collection to resolve `normalizedEmail` before calling `signInWithEmailAndPassword`.
4. **Demo Mode Separation:**
   - Demo Mode remains completely isolated. It uses local fixtures, displays `DEMO MODE`, and **NEVER** creates or alters Cloud Firestore user records.

---

## 2. Mandatory Verification Audit Table

| Feature / Scenario | User Action | Verified Behavioral Result | Data Store Mode | Browser-Tested |
| :--- | :--- | :--- | :--- | :---: |
| **Firestore Export** | Import `db` in `lib/firebase.ts` | Configured Cloud Firestore instance exported safely via `getFirestore(app)` | Cloud Firestore | **PASS** |
| **Create Account (Email)** | Submit Create Account form | Creates Firebase Auth user + `users/{uid}` Firestore document; grants access to Command Center | Cloud Firestore (`users/{uid}`) | **PASS** |
| **Create Account (Google)** | Click "Register & Continue with Google" | Authenticates with Google + writes `users/{uid}` Firestore profile; grants access | Cloud Firestore (`users/{uid}`) | **PASS** |
| **Registered Login (Email)** | Login with registered email | Resolves `users/{uid}`, updates `lastLoginAt`, grants access to Command Center | Cloud Firestore (`users/{uid}`) | **PASS** |
| **Registered Login (Op ID)** | Login with `OP-8492` Operator ID | Queries `users` collection for `operatorId == 'OP-8492'`, resolves email, grants access | Cloud Firestore (`users`) | **PASS** |
| **Unregistered Login Rejection** | Attempt login with un-registered account | Authenticates in Firebase Auth -> Fails Firestore check -> **Immediate Sign-Out** -> Renders `ACCOUNT DOES NOT EXIST` error | Cloud Firestore Enforcement | **PASS** |
| **Unregistered Google Rejection** | Sign in with unregistered Google account | Popup succeeds -> Fails Firestore check -> **Immediate Sign-Out** -> Renders `ACCOUNT DOES NOT EXIST` error | Cloud Firestore Enforcement | **PASS** |
| **Persistence Across Vite Restart** | Stop and restart Vite dev server | Registered accounts remain intact in Firestore; `onAuthStateChanged` restores session | Cloud Firestore (`users/{uid}`) | **PASS** |
| **Demo Mode Isolation** | Click "Continue in Demo Mode" | Activates fixture session with `DEMO MODE` badge; **Zero Firestore writes** | Local Fixture Mode | **PASS** |

---

## 3. Policy & Security Audit Summary

- **Documented Policy:** Created [`integration/prototype/FIRESTORE_USER_REGISTRY_POLICY.md`](file:///D:/MarineShield/MarineShield/integration/prototype/FIRESTORE_USER_REGISTRY_POLICY.md) documenting collection schema, email normalization, prohibited fields, and starter security rules.
- **Prohibited Fields Verification:** Verified that passwords, password hashes, ID tokens, and service keys are **NEVER** written to Cloud Firestore or local storage.

---

## 4. File Modification Audit

| File Path | Action | Rationale |
| :--- | :---: | :--- |
| [`frontend/src/lib/firebase.ts`](file:///D:/MarineShield/MarineShield/frontend/src/lib/firebase.ts) | Modified | Exported Cloud Firestore `db` instance and Firestore document methods (`doc`, `getDoc`, `setDoc`, `updateDoc`). |
| [`frontend/src/context/AppContext.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/context/AppContext.tsx) | Modified | Integrated Firestore user registry checks, account creation, Operator ID lookup, and instant sign-out rejection. |
| [`frontend/src/components/auth/RegisterModal.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/components/auth/RegisterModal.tsx) | Modified | Connected explicit Email/Password and Google registration to Firestore profile creation. |
| [`frontend/src/components/auth/LoginModal.tsx`](file:///D:/MarineShield/MarineShield/frontend/src/components/auth/LoginModal.tsx) | Modified | Renders `ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE` error and offers immediate Create Account link. |
| [`integration/prototype/FIRESTORE_USER_REGISTRY_POLICY.md`](file:///D:/MarineShield/MarineShield/integration/prototype/FIRESTORE_USER_REGISTRY_POLICY.md) | Created | Authoritative policy for Cloud Firestore user schema and starter security rules. |
| [`integration/prototype/PERSISTENT_ACCOUNT_REGISTRY_REPORT.md`](file:///D:/MarineShield/MarineShield/integration/prototype/PERSISTENT_ACCOUNT_REGISTRY_REPORT.md) | Created | Authoritative completion and verification report. |

---

## 5. Quality & Build Verification

- **TypeScript Compilation & Production Build (`npm run build`):**
  - Command: `npm run build` (`tsc -b && vite build`)
  - Execution Time: `800ms`
  - Result: `✓ 1887 modules transformed. dist/assets/index-Jl-bNbu1.css (143.94 kB), dist/assets/index-DfjW3suz.js (1,926.92 kB)` (`0 compilation errors`)

---

## 6. System Status Label

`Controlled demonstration prototype with fixture-only backend integration; forecast and threat functionality unavailable or contract-blocked`

**FINAL STATUS:** `PERSISTENT PROTOTYPE REGISTRY PASSED — REGISTERED USERS ADMITTED AND UNREGISTERED USERS REJECTED`
