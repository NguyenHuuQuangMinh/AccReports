const btnDeleteMultiReportCate = document.getElementById('btn-delete-multi-report-cate');
const btnDeleteAllReportCate   = document.getElementById('btn-delete-all-report-cate');

function currentQuery() {
    return window.location.search || '';
}
// bật bulk
btnDeleteMultiReportCate?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report-cate/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

btnDeleteAllReportCate?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report-cate/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// hủy
document.getElementById('btn-cancel-bulk-report-cate')?.addEventListener('click', () => {
    fetch('/admin/bulk-mode-report-cate/clear', { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
        .then(() => location.reload());
});

// tick từng dòng
document.addEventListener('change', e => {
    if (!e.target.classList.contains('row-check-report-cate')) return;

    fetch('/admin/bulk-select-report-cate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json',
                   'X-CSRFToken': getCSRFToken()},
        body: JSON.stringify({
            report_cate_id: e.target.value,
            checked: e.target.checked
        })
    })
    .then(res => res.json())
    .then(data => {
        location.reload(); // để cập nhật nút xóa
    });
});

// select all
document.getElementById('select-all-report-cate')?.addEventListener('change', function () {

    // CHECK → XÓA TẤT CẢ
    if (this.checked) {
        fetch('/admin/bulk-mode-report-cate/all' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
    // UNCHECK → QUAY VỀ XÓA NHIỀU
    else {
        fetch('/admin/bulk-mode-report-cate/multi' + currentQuery(), { method: 'POST', headers: {
            'X-CSRFToken': getCSRFToken()
        } })
            .then(() => {
        location.reload(); // để cập nhật nút xóa
    });
    }
});