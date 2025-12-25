document.getElementById('add-param').addEventListener('click', function () {
    const wrapper = document.getElementById('params-wrapper');

    const row = document.createElement('div');
    row.className = 'param-row';

    row.innerHTML = `
        <input type="hidden" name="param_id[]" value="">
        <input type="text" name="param_name[]" placeholder="Param name">
        <input type="text" name="param_value[]" placeholder="Value">
        <button type="button" class="btn remove-param">✖</button>
    `;

    wrapper.appendChild(row);
});

document.addEventListener('click', function (e) {
    if (e.target.classList.contains('remove-param')) {
        e.target.parentElement.remove();
    }
});
