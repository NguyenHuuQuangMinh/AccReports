const btnDeleteMultiReport = document.getElementById('btn-delete-multi-report');
const btnDeleteAllReport   = document.getElementById('btn-delete-all-report');

function currentQuery() {
    return window.location.search || '';
}
// bật bulk
btnDeleteMultiReport?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAllReport?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// hủy
document.getElementById('btn-cancel-bulk-report')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// tick từng dòng
document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check-report')) return;

    fetch('/admin/bulk-select-report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                   'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({
            report_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

// select all
document.getElementById('select-all-report')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode-report/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode-report/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});
