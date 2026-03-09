window.addEventListener('beforeunload', function() {
    navigator.sendBeacon('/set_offline'); // Gửi request nhẹ
});

document.addEventListener('click', function (e) {
    const toggle = document.getElementById('actionToggle');
    const menu = document.getElementById('actionMenu');

    if (toggle && toggle.contains(e.target)) {
        menu.classList.toggle('show');
        return;
    }

    if (menu && !menu.contains(e.target)) {
        menu.classList.remove('show');
    }
});
