/**
 * MagnetoCursor - Service Worker
 * 
 * Handles offline caching, background synchronization, and network request interception
 * to enable offline functionality throughout the application.
 */

// Cache names for different asset types
const CACHE_NAMES = {
  STATIC: 'magnetocursor-static-v1',
  DYNAMIC: 'magnetocursor-dynamic-v1',
  API: 'magnetocursor-api-v1'
};

// App shell assets to cache immediately on SW installation
const APP_SHELL_ASSETS = [
  '/', // Root page
  '/index.html',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/js/offline/index.js',
  '/static/js/offline/indexeddb.js',
  '/static/js/offline/sync-manager.js',
  '/static/js/offline/conflict-resolver.js',
  '/static/js/websocket-filter-ui/index.js',
  '/static/js/websocket-filter-ui/filter-builder.js',
  '/static/js/websocket-filter-ui/filter-manager.js',
  '/static/js/campaign-analytics/index.js',
  '/static/js/campaign-analytics/campaign-dashboard.js',
  '/static/js/campaign-analytics/time-series-chart.js',
  '/static/js/campaign-analytics/platform-comparison-chart.js',
  '/static/js/campaign-analytics/roi-visualization.js',
  '/static/js/campaign-analytics/kpi-metrics-panel.js',
  '/static/images/logo.png',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png',
  '/static/images/offline-banner.png',
  '/static/fonts/roboto-v20-latin-regular.woff2',
  '/static/fonts/roboto-v20-latin-500.woff2',
  '/static/fonts/roboto-v20-latin-700.woff2',
  '/manifest.json',
  '/offline.html', // Fallback page for offline mode
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/webfonts/fa-solid-900.woff2',
  'https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js'
];

// APIs to cache with network-first strategy
const API_ROUTES = [
  { url: '/api/campaigns', maxAge: 60 * 60 * 1000 }, // 1 hour
  { url: '/api/campaigns/', maxAge: 60 * 60 * 1000 }, // 1 hour (for specific campaigns)
  { url: '/api/websocket/filters', maxAge: 30 * 60 * 1000 }, // 30 minutes
  { url: '/api/websocket/filter-stats', maxAge: 15 * 60 * 1000 } // 15 minutes
];

// APIs to use background sync
const SYNC_ROUTES = [
  { url: '/api/campaigns', methods: ['POST', 'PUT', 'DELETE'] },
  { url: '/api/websocket/filters', methods: ['POST', 'PUT', 'DELETE'] }
];

// Sync tag for background sync
const SYNC_TAG = 'magnetocursor-sync';

/**
 * Install event - cache app shell assets
 */
self.addEventListener('install', event => {
  console.log('[Service Worker] Installing Service Worker...');
  
  // Skip waiting to ensure the new service worker activates immediately
  self.skipWaiting();
  
  event.waitUntil(
    caches.open(CACHE_NAMES.STATIC)
      .then(cache => {
        console.log('[Service Worker] Pre-caching App Shell');
        return cache.addAll(APP_SHELL_ASSETS);
      })
      .catch(error => {
        console.error('[Service Worker] Pre-caching failed:', error);
      })
  );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', event => {
  console.log('[Service Worker] Activating Service Worker...');
  
  // Claim clients to ensure the SW is in control immediately
  event.waitUntil(clients.claim());
  
  // Clean up old caches
  event.waitUntil(
    caches.keys()
      .then(keyList => {
        return Promise.all(keyList.map(key => {
          // If the cache name is not in our current cache names, delete it
          if (!Object.values(CACHE_NAMES).includes(key)) {
            console.log('[Service Worker] Removing old cache:', key);
            return caches.delete(key);
          }
        }));
      })
  );
  
  return self.clients.claim();
});

/**
 * Fetch event - handle network requests with appropriate strategies
 */
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Skip non-GET requests unless they are sync-eligible API requests
  if (event.request.method !== 'GET') {
    // Check if this is a sync-eligible request that should be queued when offline
    if (navigator.onLine) {
      return;
    }
    
    const isSyncRoute = SYNC_ROUTES.some(route => 
      url.pathname.startsWith(route.url) && 
      route.methods.includes(event.request.method)
    );
    
    if (isSyncRoute) {
      // Handle offline mutation by queueing for background sync
      event.respondWith(handleOfflineMutation(event.request));
    }
    
    return;
  }
  
  // Handle API requests with network-first strategy and caching
  const isApiRequest = API_ROUTES.some(route => url.pathname.startsWith(route.url));
  if (isApiRequest) {
    event.respondWith(networkFirstWithCache(event.request));
    return;
  }
  
  // Handle static assets with cache-first strategy
  if (
    url.origin === self.origin && 
    (url.pathname.startsWith('/static/') || 
     APP_SHELL_ASSETS.includes(url.pathname))
  ) {
    event.respondWith(cacheFirst(event.request));
    return;
  }
  
  // Default strategy: stale-while-revalidate
  event.respondWith(staleWhileRevalidate(event.request));
});

/**
 * Sync event - handle background sync
 */
self.addEventListener('sync', event => {
  console.log('[Service Worker] Background Sync:', event);
  
  if (event.tag === SYNC_TAG) {
    event.waitUntil(
      syncOfflineChanges()
    );
  }
});

/**
 * Push event - handle notifications
 */
self.addEventListener('push', event => {
  console.log('[Service Worker] Push Notification Received:', event);
  
  let notification = {};
  
  try {
    notification = event.data.json();
  } catch (e) {
    notification = {
      title: 'New Notification',
      body: event.data ? event.data.text() : 'No payload',
      icon: '/static/images/icon-192x192.png'
    };
  }
  
  event.waitUntil(
    self.registration.showNotification(notification.title, {
      body: notification.body,
      icon: notification.icon || '/static/images/icon-192x192.png',
      badge: '/static/images/notification-badge.png',
      data: notification.data
    })
  );
});

/**
 * Notification click event
 */
self.addEventListener('notificationclick', event => {
  console.log('[Service Worker] Notification Click:', event);
  
  event.notification.close();
  
  // Open a window/tab with this URL if provided in the notification data
  if (event.notification.data && event.notification.data.url) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  } else {
    // Otherwise, focus on an existing window or open the main page
    event.waitUntil(
      clients.matchAll({ type: 'window' })
        .then(clientList => {
          if (clientList.length > 0) {
            return clientList[0].focus();
          }
          return clients.openWindow('/');
        })
    );
  }
});

/**
 * Cache-first strategy
 * Tries to serve from cache first, falls back to network
 */
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    await updateCache(CACHE_NAMES.STATIC, request, networkResponse.clone());
    return networkResponse;
  } catch (error) {
    console.error('[Service Worker] Cache first fetch failed:', error);
    
    // Return offline page if it's an HTML request
    if (request.headers.get('Accept').includes('text/html')) {
      return caches.match('/offline.html');
    }
    
    // Otherwise, return a fallback response or error
    return new Response('Network error happened', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

/**
 * Network-first with cache strategy
 * Tries network first, falls back to cache, updates cache with fresh content
 */
async function networkFirstWithCache(request) {
  // Find the API route that matches this request
  const apiRoute = API_ROUTES.find(route => request.url.includes(route.url));
  const cacheName = CACHE_NAMES.API;
  
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Clone the response to store in cache
    await updateCache(cacheName, request, networkResponse.clone());
    
    return networkResponse;
  } catch (error) {
    console.log('[Service Worker] Network request failed, falling back to cache');
    
    // If network fails, try from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      // Check cache age if a maxAge is specified for this route
      if (apiRoute && apiRoute.maxAge) {
        const cacheDate = new Date(cachedResponse.headers.get('sw-cache-date'));
        const ageInMs = Date.now() - cacheDate.getTime();
        
        // If cache is too old, return a special response
        if (ageInMs > apiRoute.maxAge) {
          return new Response(JSON.stringify({
            error: 'offline-stale-data',
            cachedAt: cacheDate.toISOString(),
            data: await cachedResponse.clone().json()
          }), {
            headers: { 'Content-Type': 'application/json' }
          });
        }
      }
      
      return cachedResponse;
    }
    
    // If no cache, return offline JSON response
    return new Response(JSON.stringify({
      error: 'offline',
      message: 'You are offline and this content is not available in cache'
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Stale-while-revalidate strategy
 * Returns cached version immediately, then updates cache in background
 */
async function staleWhileRevalidate(request) {
  const cache = await caches.open(CACHE_NAMES.DYNAMIC);
  
  // Try to get from cache
  const cachedResponse = await cache.match(request);
  
  // Create a promise to update the cache
  const updateCachePromise = fetch(request)
    .then(networkResponse => {
      cache.put(request, networkResponse.clone());
      return networkResponse;
    })
    .catch(error => {
      console.log('[Service Worker] Stale-while-revalidate network fetch failed');
      
      // If it's an HTML request and we couldn't fetch, return offline page
      if (request.headers.get('Accept').includes('text/html')) {
        return caches.match('/offline.html');
      }
      
      // For other types, we don't do anything special as we already returned the cached response
      throw error;
    });
  
  // Return the cached response or wait for the network
  return cachedResponse || updateCachePromise;
}

/**
 * Update cache with a new response
 */
async function updateCache(cacheName, request, response) {
  // Only cache valid responses
  if (!response || response.status !== 200) {
    return;
  }
  
  const cache = await caches.open(cacheName);
  
  // Add current timestamp to the response headers for cache age tracking
  const responseToCache = new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: new Headers(response.headers)
  });
  responseToCache.headers.set('sw-cache-date', new Date().toISOString());
  
  await cache.put(request, responseToCache);
}

/**
 * Handle offline mutation by storing in IndexedDB for later syncing
 */
async function handleOfflineMutation(request) {
  // Clone the request data
  const requestData = await request.clone().text();
  
  // Store the request in IndexedDB for later sync
  await storeOfflineRequest({
    url: request.url,
    method: request.method,
    headers: Array.from(request.headers.entries()),
    body: requestData,
    timestamp: Date.now()
  });
  
  // Register for background sync
  await self.registration.sync.register(SYNC_TAG);
  
  // Return a mock success response
  return new Response(JSON.stringify({
    success: true,
    offline: true,
    message: 'Your changes have been saved offline and will sync when you reconnect'
  }), {
    status: 202, // Accepted
    headers: { 'Content-Type': 'application/json' }
  });
}

/**
 * Store offline request in IndexedDB
 */
async function storeOfflineRequest(requestData) {
  // We'll use a simple localStorage approach here for the service worker
  // In the full implementation, this would use IndexedDB through the indexeddb.js module
  
  return new Promise((resolve, reject) => {
    // Open a connection to the offline-requests database
    const dbPromise = indexedDB.open('offline-requests', 1);
    
    dbPromise.onupgradeneeded = function(event) {
      const db = event.target.result;
      
      // Create an object store for offline requests if it doesn't exist
      if (!db.objectStoreNames.contains('requests')) {
        db.createObjectStore('requests', { keyPath: 'id', autoIncrement: true });
      }
    };
    
    dbPromise.onsuccess = function(event) {
      const db = event.target.result;
      const transaction = db.transaction('requests', 'readwrite');
      const store = transaction.objectStore('requests');
      
      // Add the request to the store
      const request = store.add(requestData);
      
      request.onsuccess = function() {
        console.log('[Service Worker] Offline request stored successfully');
        resolve();
      };
      
      request.onerror = function(error) {
        console.error('[Service Worker] Error storing offline request:', error);
        reject(error);
      };
      
      transaction.oncomplete = function() {
        db.close();
      };
    };
    
    dbPromise.onerror = function(error) {
      console.error('[Service Worker] Error opening IndexedDB:', error);
      reject(error);
    };
  });
}

/**
 * Sync offline changes when back online
 */
async function syncOfflineChanges() {
  // We'll retrieve the stored requests from IndexedDB and attempt to replay them
  
  return new Promise((resolve, reject) => {
    const dbPromise = indexedDB.open('offline-requests', 1);
    
    dbPromise.onsuccess = function(event) {
      const db = event.target.result;
      const transaction = db.transaction('requests', 'readwrite');
      const store = transaction.objectStore('requests');
      
      // Get all stored requests
      const requestsQuery = store.getAll();
      
      requestsQuery.onsuccess = async function() {
        const requests = requestsQuery.result;
        console.log(`[Service Worker] Found ${requests.length} offline requests to sync`);
        
        // Process each request
        for (const storedRequest of requests) {
          try {
            // Recreate the request
            const request = new Request(storedRequest.url, {
              method: storedRequest.method,
              headers: new Headers(storedRequest.headers),
              body: storedRequest.body,
              credentials: 'include'
            });
            
            // Attempt to send the request
            const response = await fetch(request);
            
            if (response.ok) {
              console.log(`[Service Worker] Successfully synced request to ${storedRequest.url}`);
              
              // Delete the successful request from the store
              store.delete(storedRequest.id);
            } else {
              console.error(`[Service Worker] Failed to sync request: ${response.status}`);
              
              // Keep the request in the store to try again later
              // but update the timestamp to track retry attempts
              storedRequest.lastRetry = Date.now();
              storedRequest.retryCount = (storedRequest.retryCount || 0) + 1;
              store.put(storedRequest);
            }
          } catch (error) {
            console.error('[Service Worker] Error during sync:', error);
            // Keep the request for later retry
          }
        }
        
        resolve();
      };
      
      requestsQuery.onerror = function(error) {
        console.error('[Service Worker] Error retrieving offline requests:', error);
        reject(error);
      };
      
      transaction.oncomplete = function() {
        db.close();
      };
    };
    
    dbPromise.onerror = function(error) {
      console.error('[Service Worker] Error opening IndexedDB:', error);
      reject(error);
    };
  });
}
