import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import {
  auth,
  db,
  googleProvider,
  hasFirebaseConfig,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
  sendPasswordResetEmail,
  signOut as firebaseSignOut,
  updateProfile,
  onAuthStateChanged,
  doc,
  getDoc,
  setDoc,
  updateDoc,
  serverTimestamp,
  collection,
  query,
  where,
  getDocs,
  type FirebaseUser,
} from '../lib/firebase';

export interface AppNotification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  createdAt: string;
  read: boolean;
  source?: string;
}

export interface UserSession {
  userId: string;
  userName: string;
  email?: string;
  role: string;
  loginTime: string;
  isDemoMode?: boolean;
}

export interface MapTarget {
  center: [number, number];
  zoom?: number;
  timestamp: number;
}

interface AppContextType {
  user: UserSession | null;
  firebaseUser: FirebaseUser | null;
  isDemoMode: boolean;
  hasFirebaseConfig: boolean;
  loginDemo: () => void;
  logout: () => Promise<void>;
  registerWithEmail: (name: string, opId: string, email: string, pass: string) => Promise<void>;
  registerWithGoogle: (opId?: string) => Promise<void>;
  loginWithEmailOrId: (identifier: string, pass: string) => Promise<void>;
  loginWithGoogle: () => Promise<void>;
  sendPasswordReset: (email: string) => Promise<void>;
  notifications: AppNotification[];
  unreadCount: number;
  markAllAsRead: () => void;
  addNotification: (notif: Omit<AppNotification, 'createdAt' | 'read'> & { id?: string }) => void;
  clearNotifications: () => void;
  mapTarget: MapTarget | null;
  flyToCoordinate: (lat: number, lon: number, zoom?: number) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

const STORAGE_KEY_USER = 'marineshield_user_session';
const STORAGE_KEY_NOTIFS = 'marineshield_notifications';

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [mapTarget, setMapTarget] = useState<MapTarget | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isDemoMode, setIsDemoMode] = useState<boolean>(() => {
    try {
      return localStorage.getItem('marineshield_demo_mode') === 'true';
    } catch {
      return false;
    }
  });

  const [user, setUser] = useState<UserSession | null>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_USER);
      if (stored) return JSON.parse(stored);
    } catch {
      // ignore
    }
    return null;
  });

  useEffect(() => {
    if (!auth) return;
    const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
      setFirebaseUser(fbUser);
      if (fbUser) {
        setIsDemoMode(false);
        localStorage.removeItem('marineshield_demo_mode');

        // Check Cloud Firestore Registry
        if (db) {
          try {
            const userRef = doc(db, 'users', fbUser.uid);
            const userSnap = await getDoc(userRef);

            if (!userSnap.exists() || userSnap.data()?.accountStatus !== 'ACTIVE') {
              // Unregistered user -> Sign out immediately
              if (auth) await firebaseSignOut(auth);
              setUser(null);
              localStorage.removeItem(STORAGE_KEY_USER);
              return;
            }

            const data = userSnap.data();
            const session: UserSession = {
              userId: data.operatorId || fbUser.uid.slice(0, 8).toUpperCase(),
              userName: data.displayName || fbUser.displayName || 'Authenticated Operator',
              email: fbUser.email || undefined,
              role: 'Registered Operator',
              loginTime: new Date().toISOString(),
              isDemoMode: false,
            };
            setUser(session);
            localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(session));

            // Update lastLoginAt
            await updateDoc(userRef, { lastLoginAt: serverTimestamp() });
          } catch (err) {
            console.error('Error verifying Firestore user registry:', err);
          }
        } else {
          // Fallback if db is not ready
          const session: UserSession = {
            userId: fbUser.uid.slice(0, 8).toUpperCase(),
            userName: fbUser.displayName || fbUser.email?.split('@')[0] || 'Authenticated Operator',
            email: fbUser.email || undefined,
            role: 'Firebase Operator',
            loginTime: new Date().toISOString(),
            isDemoMode: false,
          };
          setUser(session);
          localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(session));
        }
      } else if (!isDemoMode) {
        setUser(null);
        localStorage.removeItem(STORAGE_KEY_USER);
      }
    });
    return () => unsubscribe();
  }, [isDemoMode]);

  const flyToCoordinate = (lat: number, lon: number, zoom: number = 9) => {
    setMapTarget({
      center: [lon, lat],
      zoom,
      timestamp: Date.now(),
    });
  };

  const loginDemo = () => {
    setIsDemoMode(true);
    localStorage.setItem('marineshield_demo_mode', 'true');
    const demoSession: UserSession = {
      userId: 'OP-8492',
      userName: 'Demo Operator',
      role: 'Command Operator (DEMO)',
      loginTime: new Date().toISOString(),
      isDemoMode: true,
    };
    setUser(demoSession);
    localStorage.setItem(STORAGE_KEY_USER, JSON.stringify(demoSession));
  };

  const registerWithEmail = async (name: string, opId: string, emailStr: string, passStr: string) => {
    if (!auth) throw new Error('Firebase Auth is unconfigured');
    const cred = await createUserWithEmailAndPassword(auth, emailStr.trim(), passStr);
    if (cred.user) {
      await updateProfile(cred.user, { displayName: name });
      if (db) {
        const userRef = doc(db, 'users', cred.user.uid);
        await setDoc(userRef, {
          uid: cred.user.uid,
          normalizedEmail: emailStr.trim().toLowerCase(),
          displayName: name,
          operatorId: opId || `OP-${cred.user.uid.slice(0, 4).toUpperCase()}`,
          provider: 'password',
          accountStatus: 'ACTIVE',
          createdAt: serverTimestamp(),
          lastLoginAt: serverTimestamp(),
          registryVersion: '1.0-prototype',
        });
      }
    }
  };

  const registerWithGoogle = async (opId?: string) => {
    if (!auth || !googleProvider) throw new Error('Firebase Auth or Google Provider unconfigured');
    const cred = await signInWithPopup(auth, googleProvider);
    if (cred.user && db) {
      const userRef = doc(db, 'users', cred.user.uid);
      await setDoc(userRef, {
        uid: cred.user.uid,
        normalizedEmail: (cred.user.email || '').toLowerCase(),
        displayName: cred.user.displayName || 'Google Operator',
        operatorId: opId || `OP-${cred.user.uid.slice(0, 4).toUpperCase()}`,
        provider: 'google',
        accountStatus: 'ACTIVE',
        createdAt: serverTimestamp(),
        lastLoginAt: serverTimestamp(),
        registryVersion: '1.0-prototype',
      });
    }
  };

  const loginWithEmailOrId = async (identifier: string, passStr: string) => {
    if (!auth) throw new Error('Firebase Auth is unconfigured');

    let targetEmail = identifier.trim();
    if (!targetEmail.includes('@') && db) {
      // Lookup email by Operator ID in Firestore
      const usersRef = collection(db, 'users');
      const q = query(usersRef, where('operatorId', '==', identifier.trim()));
      const querySnap = await getDocs(q);

      if (querySnap.empty) {
        throw new Error('ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE');
      }
      targetEmail = querySnap.docs[0].data().normalizedEmail;
    }

    const cred = await signInWithEmailAndPassword(auth, targetEmail, passStr);

    // Verify Firestore Profile
    if (cred.user && db) {
      const userRef = doc(db, 'users', cred.user.uid);
      const userSnap = await getDoc(userRef);

      if (!userSnap.exists() || userSnap.data()?.accountStatus !== 'ACTIVE') {
        await firebaseSignOut(auth);
        throw new Error('ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE');
      }
    }
  };

  const loginWithGoogle = async () => {
    if (!auth || !googleProvider) throw new Error('Firebase Auth or Google Provider unconfigured');
    const cred = await signInWithPopup(auth, googleProvider);

    if (cred.user && db) {
      const userRef = doc(db, 'users', cred.user.uid);
      const userSnap = await getDoc(userRef);

      if (!userSnap.exists() || userSnap.data()?.accountStatus !== 'ACTIVE') {
        await firebaseSignOut(auth);
        throw new Error('ACCOUNT DOES NOT EXIST — CREATE AN ACCOUNT TO CONTINUE');
      }
    }
  };

  const sendPasswordReset = async (emailStr: string) => {
    if (!auth) throw new Error('Firebase Auth is unconfigured');
    await sendPasswordResetEmail(auth, emailStr.trim());
  };

  const logout = async () => {
    if (auth && firebaseUser) {
      await firebaseSignOut(auth);
    }
    setIsDemoMode(false);
    setUser(null);
    localStorage.removeItem('marineshield_demo_mode');
    localStorage.removeItem(STORAGE_KEY_USER);
  };

  const [notifications, setNotifications] = useState<AppNotification[]>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY_NOTIFS);
      if (stored) return JSON.parse(stored);
    } catch {
      // ignore
    }
    return [
      {
        id: 'notif-welcome-init',
        title: 'Welcome to MarineShield',
        message: 'Your command center is ready.',
        type: 'info',
        createdAt: new Date().toISOString(),
        read: false,
      },
    ];
  });

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => (n.read ? n : { ...n, read: true })));
  };

  const addNotification = (
    notifData: Omit<AppNotification, 'createdAt' | 'read'> & { id?: string }
  ) => {
    const id = notifData.id || `notif-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
    setNotifications((prev) => {
      if (prev.some((n) => n.id === id)) return prev;
      return [
        {
          id,
          title: notifData.title,
          message: notifData.message,
          type: notifData.type || 'info',
          source: notifData.source,
          createdAt: new Date().toISOString(),
          read: false,
        },
        ...prev,
      ];
    });
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <AppContext.Provider
      value={{
        user,
        firebaseUser,
        isDemoMode,
        hasFirebaseConfig,
        loginDemo,
        logout,
        registerWithEmail,
        registerWithGoogle,
        loginWithEmailOrId,
        loginWithGoogle,
        sendPasswordReset,
        notifications,
        unreadCount,
        markAllAsRead,
        addNotification,
        clearNotifications,
        mapTarget,
        flyToCoordinate,
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = (): AppContextType => {
  const context = useContext(AppContext);
  if (!context) throw new Error('useApp must be used within an AppProvider');
  return context;
};
