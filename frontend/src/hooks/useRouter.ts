import { useState, useEffect, useCallback } from 'react';

/**
 * Minimal client-side router using the native History API.
 * Listens to popstate (browser back/forward) and exposes navigate().
 */
export function useRouter() {
  const [path, setPath] = useState(() => window.location.pathname);

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname);
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

  const navigate = useCallback((to: string) => {
    if (to !== window.location.pathname) {
      window.history.pushState(null, '', to);
      setPath(to);
    }
  }, []);

  return { path, navigate };
}
