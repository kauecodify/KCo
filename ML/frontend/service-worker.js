// KCo ML Service Worker
// Version: 1.0.0
// Old But Gold TR8 IVSTO

const CACHE_NAME = 'kco-ml-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/index.html',
  '/manifest.json',
  '/styles.css',
  'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Rajdhani:wght@300;400;500;600;700&display=swap'
];

// Install
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('Caching assets...');
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => {
        console.log('Assets cached successfully');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('Cache failed:', error);
      })
  );
});

// Activate
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
    .then(() => {
      console.log('Service Worker activated');
      return self.clients.claim();
    })
  );
});

// Fetch
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        if (response) {
          console.log('Serving from cache:', event.request.url);
          return response;
        }
        console.log('Fetching from network:', event.request.url);
        return fetch(event.request);
      })
      .catch((error) => {
        console.error('Fetch failed:', error);
        // Return a fallback response for failed requests
        if (event.request.destination === 'document') {
          return caches.match('/index.html');
        }
      })
  );
});

// Background sync for offline uploads
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-images') {
    event.waitUntil(syncImages());
  }
});

async function syncImages() {
  const pendingImages = await getPendingImages();
  
  for (const image of pendingImages) {
    try {
      // In a real implementation, this would call your API
      console.log('Syncing image:', image.id);
      await uploadImage(image);
      await removePendingImage(image.id);
    } catch (error) {
      console.error('Failed to sync image:', image.id, error);
    }
  }
}

// Message listener for communication with the page
self.addEventListener('message', (event) => {
  if (event.data.type === 'CACHE_IMAGE') {
    caches.open(CACHE_NAME)
      .then((cache) => {
        cache.put(event.data.url, event.data.response);
      });
  }
  
  if (event.data.type === 'REGISTER_SYNC') {
    self.registration.sync.register(event.data.tag);
  }
});

// Helper functions (would be implemented in a real app)
async function getPendingImages() {
  // Get images stored in IndexedDB or localStorage
  return [];
}

async function uploadImage(image) {
  // Upload to server
  return true;
}

async function removePendingImage(id) {
  // Remove from local storage
  return true;
}

// Push notification support
self.addEventListener('push', (event) => {
  const data = event.data.json();
  const options = {
    body: data.body,
    icon: '/icon-192x192.png',
    badge: '/badge-72x72.png',
    data: {
      url: data.url || '/'
    }
  };
  
  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  
  if (event.notification.data.url) {
    event.waitUntil(
      clients.openWindow(event.notification.data.url)
    );
  }
});

// Background fetch for large images
self.addEventListener('backgroundfetchsuccess', (event) => {
  const record = event.record;
  const response = event.response;
  
  // Cache the response for later use
  caches.open(CACHE_NAME)
    .then((cache) => {
      cache.put(record.request, response.clone());
    });
});

console.log('KCo ML Service Worker loaded - Old But Gold TR8 IVSTO');
