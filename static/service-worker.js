.addEventListener('install', function(e) {
console.log('Service Worker: Installed');
});
self
self.addEventListener('fetch', function(e) {
// Puedes agregar cache si quieres que funcione offline
console.log('Service Worker: Fetching ', e.request.url);
});
