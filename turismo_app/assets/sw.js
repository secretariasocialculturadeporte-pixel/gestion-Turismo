// Basic Service Worker for caching app assets

const CACHE_NAME = 'turismo-app-cache-v1';
// Lista de archivos para cachear. Debería incluir el icono, el manifest, y los assets principales.
const urlsToCache = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icons/logo_app_login_192.png',
  '/icons/logo_app_login_512.png'
  // Agrega aquí otros assets importantes como CSS o JS si los tuvieras.
];

// Evento de instalación: se dispara cuando el SW se instala.
self.addEventListener('install', event => {
  console.log('Service Worker: Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Service Worker: Cache abierto, añadiendo assets principales.');
        return cache.addAll(urlsToCache);
      })
      .then(() => {
        console.log('Service Worker: Todos los assets fueron cacheados exitosamente.');
        return self.skipWaiting(); // Forzar la activación del nuevo SW
      })
  );
});

// Evento de activación: se dispara cuando el SW se activa.
// Es un buen lugar para limpiar cachés antiguas.
self.addEventListener('activate', event => {
  console.log('Service Worker: Activando...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Limpiando caché antigua:', cache);
            return caches.delete(cache);
          }
        })
      );
    })
  );
  return self.clients.claim(); // Tomar control de las páginas abiertas
});

// Evento fetch: se dispara cada vez que la página hace una petición de red.
// Estrategia: "Cache first, then network".
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Si la respuesta está en el caché, la retornamos.
        if (response) {
          console.log('Service Worker: Sirviendo desde caché:', event.request.url);
          return response;
        }
        // Si no, hacemos la petición a la red.
        console.log('Service Worker: Petición a red para:', event.request.url);
        return fetch(event.request);
      }
    )
  );
});
