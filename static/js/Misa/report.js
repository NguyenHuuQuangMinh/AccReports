document.getElementById('add-param').addEventListener('click', function () {
    const wrapper = document.getElementById('params-wrapper');
    const index = wrapper.children.length;
    const row = document.createElement('div');
    row.className = 'param-row';

    row.innerHTML = `
        <input type="hidden" name="param_id[]" value="">
        <input type="text" name="param_name[]" class="param-name" placeholder="Tên Param">

                <input type="text" name="param_value[]" class="param-value" placeholder="Giá trị mặc định">

                <input type="text" name="param_label[]" class="param-label" placeholder="Label hiển thị (VD: Từ ngày)">

                <select name="param_type[]" class="param-type">
                    <option value="string">Text</option>
                    <option value="int">Số nguyên</option>
                    <option value="decimal">Số thập phân</option>
                    <option value="date">Ngày</option>
                    <option value="datetime">Ngày & giờ</option>
                </select>
                <label class="param-flag">
                    <input type="checkbox" name="allow_null[${index}]" value="1">
                    Null
                </label>

                <label class="param-flag">
                    <input type="checkbox" name="allow_all[${index}]" value="1">
                    All
                </label>

                <button type="button" class="btn remove-param">✖</button>
    `;

    wrapper.appendChild(row);
});

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('remove-param')) {
        e.target.parentElement.remove();
    }
});

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.desc-text').forEach(desc => {
        // đợi browser render xong mới đo
        requestAnimationFrame(() => {
            if (desc.scrollHeight > desc.clientHeight + 1) {
                desc.classList.add('clamped');
            }
        });
    });
});

