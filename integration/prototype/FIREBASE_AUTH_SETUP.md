# Firebase Authentication Setup Guide

**Target System:** MarineShield Frontend (`D:\MarineShield\MarineShield\frontend\`)  
**Document Purpose:** Production Firebase Authentication & Firestore configuration specification for MarineShield deployment.  
**Created Timestamp:** 2026-08-23 (UTC)  
**Security Status:** NO SECRETS OR HARD-CODED CREDENTIALS INCLUDED

---

## 1. Firebase Project Prerequisites

To enable live Firebase Authentication for MarineShield, configure a Firebase project in the [Firebase Console](https://console.firebase.google.com/):

1. **Enable Authentication Providers:**
   - **Email/Password:** Enable standard Email/Password sign-in method.
   - **Google Sign-In:** Enable Google identity provider.
2. **Authorized Domains:**
   - Add deployment domain (e.g., `localhost`, `marineshield.app`) under Firebase Auth Settings -> Authorized Domains.

---

## 2. Environment Variable Configuration

Create `.env.local` in `frontend/` using these placeholder variable names:

```env
VITE_FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY_PLACEHOLDER
VITE_FIREBASE_AUTH_DOMAIN=YOUR_PROJECT_ID.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=YOUR_PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=YOUR_PROJECT_ID.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=YOUR_MESSAGING_SENDER_ID
VITE_FIREBASE_APP_ID=YOUR_APP_ID
```

> [!IMPORTANT]
> Never commit actual API keys or secret values into Git repositories. Environment variables must be injected during build time or deployment pipelines.

---

## 3. Package Installation Requirement

When ready to enable Firebase SDK support, run:

```bash
npm install firebase
```

---

## 4. Prototype Demo Fallback

In the current prototype build, Firebase SDK dependencies are not installed. The application operates in **DEMO MODE** with explicit disclosures:
- Labeled: `DEMO ONLY — NO AUTHENTICATED ACCESS`
- All data sources labeled: `SYNTHETIC_DEVELOPMENT_FIXTURE` / `MOCK_HYBRID`
