const btnDeleteMultiRole = document.getElementById('btn-delete-multi-role');
const btnDeleteAllRole   = document.getElementById('btn-delete-all-role');

function currentQueryRole() {
    return window.location.search || '';
}

// bật bulk
btnDeleteMultiRole?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-role/multi' + currentQueryRole(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAllRole?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-role/all' + currentQueryRole(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// hủy
document.getElementById('btn-cancel-bulk-role')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-role/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// tick từng dòng
document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check-role')) return;

    fetch('/admin/bulk-select-role', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({
            role_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

// select all
document.getElementById('select-all-role')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode-role/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode-role/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});
