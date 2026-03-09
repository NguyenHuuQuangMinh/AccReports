const btnDeleteMulti = document.getElementById('btn-delete-multi');
const btnDeleteAll   = document.getElementById('btn-delete-all');

function currentQuery() {
    return window.location.search || '';
}

// bật bulk
btnDeleteMulti?.addEventListener('click', () => {
    fetch('/admin/bulk-mode/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAll?.addEventListener('click', () => {
    fetch('/admin/bulk-mode/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// hủy
document.getElementById('btn-cancel-bulk')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// tick từng dòng
document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check')) return;

    fetch('/admin/bulk-select', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
        body: JSON.stringify({
            user_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

// select all
document.getElementById('select-all')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode/all' + currentQuery(), { method: 'POST' , headers: {
            'X-CSRFToken': getCSRFToken()
        }})
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode/multi' + currentQuery(), { method: 'POST' , headers: {
            'X-CSRFToken': getCSRFToken()
        }})
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});