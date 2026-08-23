import { MockApiClient } from './clients/MockApiClient';
import { FastApiClient } from './clients/FastApiClient';
import type { ApiClient } from './clients/ApiClient';

// Default to MockApiClient for Track A local demonstration.
// FastApiClient is used ONLY when VITE_API_MODE is explicitly set to 'live' or 'fastapi'.
const apiMode = import.meta.env.VITE_API_MODE;

export const api: ApiClient = 
  (apiMode === 'live' || apiMode === 'fastapi')
    ? new FastApiClient() 
    : new MockApiClient();
