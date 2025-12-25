window.addEventListener('beforeunload', function() {
    navigator.sendBeacon('/set_offline'); // Gửi request nhẹ
});
