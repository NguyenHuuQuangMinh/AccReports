function moveToAvailable(id){
    const li = document.querySelector(`#assigned-list li[data-id="${id}"]`);
    const available = document.getElementById('available-list');
    if (!li || !available) return;

    // bỏ hidden input
    li.querySelector('input')?.remove();

    // đổi nút ➖ thành ➕ và đổi onclick
    const btn = li.querySelector("button");
    btn.textContent = "➕";
    btn.setAttribute("onclick", `moveToAssigned(${id})`);

    available.appendChild(li);
}


function moveToAssigned(id){
    const li = document.querySelector(`#available-list li[data-id="${id}"]`);
    const assigned = document.getElementById('assigned-list');
    if (!li || !assigned) return;

    // Nếu đã có hidden rồi thì không tạo thêm
    if (!li.querySelector('input')) {
        const hidden = document.createElement("input");
        hidden.type = "hidden";
        hidden.name = "assigned[]";
        hidden.value = id;
        li.appendChild(hidden);
    }

    const btn = li.querySelector("button");
    btn.textContent = "➖";
    btn.setAttribute("onclick", `moveToAvailable(${id})`);

    assigned.appendChild(li);
}

function filterList(inputId, listId) {
    const keyword = document.getElementById(inputId).value.toLowerCase();
    const items = document.querySelectorAll(`#${listId} li`);

    items.forEach(li => {
        const text = li.querySelector("span").textContent.toLowerCase();
        li.style.display = text.includes(keyword) ? "" : "none";
    });
}

document.getElementById("search-assigned")
    .addEventListener("input", () => filterList("search-assigned", "assigned-list"));

document.getElementById("search-available")
    .addEventListener("input", () => filterList("search-available", "available-list"));