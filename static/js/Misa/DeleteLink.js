const btnDeleteMultiBrand = document.getElementById('btn-delete-multi-brands');
const btnDeleteAllBrand   = document.getElementById('btn-delete-all-brands');
const btnDeleteMultiLink = document.getElementById('btn-delete-multi-links');
const btnDeleteAllLink   = document.getElementById('btn-delete-all-links');

function currentQueryBrand() {
    return window.location.search || '';
}

// bật bulk
btnDeleteMultiBrand?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-brands/multi' + currentQueryBrand(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAllBrand?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-brands/all' + currentQueryBrand(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteMultiLink?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-links/multi' + currentQueryBrand(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAllLink?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-links/all' + currentQueryBrand(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// hủy
document.getElementById('btn-cancel-bulk-brands')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-brands/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

document.getElementById('btn-cancel-bulk-links')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-links/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// tick từng dòng
document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check-brand')) return;

    fetch('/admin/bulk-select-brands', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',headers: {
            'X-CSRFToken': getCSRFToken()
        }  },
        body: JSON.stringify({
            brand_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check-link')) return;

    fetch('/admin/bulk-select-links', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                   'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({
            link_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

// select all
document.getElementById('select-all-brands')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode-brands/all' + currentQuery(), { method: 'POST' , headers: {
            'X-CSRFToken': getCSRFToken()
        }})
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode-brands/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});

// select all
document.getElementById('select-all-links')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode-links/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode-links/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});
