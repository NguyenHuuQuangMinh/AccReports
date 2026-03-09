function moveToAvailableCate(id){
    const li = document.querySelector(`#assigned-list-cate li[data-id="${id}"]`);
    const available = document.getElementById('available-list-cate');
    if (!li || !available) return;

    // bỏ hidden input
    li.querySelector('input')?.remove();

    // đổi nút ➖ thành ➕ và đổi onclick
    const btn = li.querySelector("button");
    btn.textContent = "➕";
    btn.setAttribute("onclick", `moveToAssignedCate(${id})`);

    available.appendChild(li);
}


function moveToAssignedCate(id){
    const li = document.querySelector(`#available-list-cate li[data-id="${id}"]`);
    const assigned = document.getElementById('assigned-list-cate');
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
    btn.setAttribute("onclick", `moveToAvailableCate(${id})`);

    assigned.appendChild(li);
}

function filterListCate(inputId, listId) {
    const keyword = document.getElementById(inputId).value.toLowerCase();
    const items = document.querySelectorAll(`#${listId} li`);

    items.forEach(li => {
        const text = li.querySelector("span").textContent.toLowerCase();
        li.style.display = text.includes(keyword) ? "" : "none";
    });
}

document.getElementById("search-assigned-cate")
    .addEventListener("input", () => filterListCate("search-assigned-cate", "assigned-list-cate"));

document.getElementById("search-available-cate")
    .addEventListener("input", () => filterListCate("search-available-cate", "available-list-cate"));