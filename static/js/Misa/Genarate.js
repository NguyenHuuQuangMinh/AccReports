function getCSRFToken() {
    return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}
function toggleDesc(id) {
    const overlay = document.getElementById(`overlay-${id}`);
    if (overlay) {
        overlay.classList.toggle('show');
    }
}

function toggleApiKey(el) {
    const span = el.parentElement.querySelector('.api-key, .api-key-report');
    const icon = el.querySelector('i');
    if (span.classList.contains("masked")) {
        // hiện key thật
        span.classList.remove("masked");
        span.textContent = span.dataset.key;
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
    } else {
        // che nhưng vẫn đúng length thật
        span.classList.add("masked");
        span.textContent = span.dataset.key;
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");

    }
}

function copyApiKey(el) {
    const span = el.parentElement.querySelector('.api-key, .api-key-report');
    const key = span.dataset.key;

    if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(key).then(() => {
            sendFlashSuccess();
        }).catch(err => {
            console.error("Không copy được: ", err);
        });
    } else {
        // fallback cho trình duyệt không hỗ trợ clipboard API
        const tempInput = document.createElement("input");
        tempInput.value = key;
        document.body.appendChild(tempInput);
        tempInput.select();
        tempInput.setSelectionRange(0, 99999); // cho mobile
        document.execCommand("copy");
        document.body.removeChild(tempInput);
        sendFlashSuccess();
    }
}

function sendFlashSuccess() {
    fetch("/flash/copy-success", {
        method: "POST",
        headers: {
            'X-CSRFToken': getCSRFToken()
        },
        credentials: "include"   // 👈 đảm bảo gửi cookie session
    }).then(() => {
        location.reload();
    });
}

function openApiPopup(reportId){
    fetch("/api_keys/json")
        .then(res => res.json())
        .then(keys => {
            const ul = document.getElementById("apiList");
            ul.innerHTML = "";

            keys.forEach(k => {
                const li = document.createElement("li");
                li.className = "api-item";
                li.onclick = () => selectApi(reportId, k.Id);

                li.innerHTML = `
                    <div class="api-title">${k.AppName}</div>
                    <div class="api-sub">ID: ${k.Id}</div>
                `;

                ul.appendChild(li);
            });

            document.getElementById("apiModalWrapper").style.display = "flex";
        });
}

function closeApiPopup(){
    document.getElementById("apiModalWrapper").style.display = "none";
}

function selectApi(reportId, apiKeyId){
    // chuyển sang route tạo API_report
    window.location.href = `/user/create-api-link/${reportId}/${apiKeyId}`;
}

function openDetail(action_choice){
    const params = new URLSearchParams(window.location.search)
    if(!params.get("action")){
        const selected = document.querySelector("select[name=action]");
        if (selected && selected.value){
            params.set("action", selected.value);
        }
    }

    params.set("action_choice", action_choice);
    fetch(`/admin/history-detail?${params.toString()}`)
        .then(res => res.text())
        .then(html => {
            document.getElementById("modal-body").innerHTML = html;
            document.getElementById("detailModal").style.display = "block";
        })
}

function closeModal(){
    document.getElementById("detailModal").style.display = "none";
}

function openAddLinkModal(brandId, brandName) {
    document.getElementById('modal-brand-id').value = brandId;
    document.getElementById('modal-title').innerText = `➕ Thêm Link cho ${brandName}`;
    document.getElementById('addLinkModal').classList.remove('hidden');
}

function closeModalLink() {
    const modal = document.getElementById('addLinkModal');
    const form  = document.getElementById('add-link-form');
    const list  = document.getElementById('link-list');
    form.reset();
    list.innerHTML = `
        <div class="link-row">
            <div class="input-group">
                <span class="icon">🔤</span>
                <input type="text" name="names[]" placeholder="Tên link" required>
            </div>
    
            <div class="input-group">
                <span class="icon">🔗</span>
                <input type="text" name="urls[]" placeholder="URL" required>
            </div>
            
            <button type="button" class="btn-remove" onclick="removeLinkRow(this)">✖</button>
        </div>
    `;
    modal.classList.add('hidden');
}

function addLinkRow() {
    const div = document.createElement('div');
    div.className = 'link-row';
    div.innerHTML = `
        <div class="input-group">
            <span class="icon">🔤</span>
            <input type="text" name="names[]" placeholder="Tên link" required>
        </div>

        <div class="input-group">
            <span class="icon">🔗</span>
            <input type="text" name="urls[]" placeholder="URL" required>
        </div>
        
        <button type="button" class="btn-remove" onclick="removeLinkRow(this)">✖</button>
    `;
    document.getElementById('link-list').appendChild(div);
}

function removeLinkRow(btn) {
    btn.closest('.link-row').remove();
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('add-link-form');
    if (!form) return;

    form.addEventListener('submit', e => {
        e.preventDefault();
        const fd = new FormData(form);
        fd.append('modal', '1')
        fetch('/admin/create-link', {
            method: 'POST',
            headers: {
            'X-CSRFToken': getCSRFToken()
            },
            body: fd
        })
        .then(res => res.json())
        .then(data => {
            if(data.success){
                showToast(data.message, 'success');
                closeModalLink();
            }else{
                showToast(data.message, 'error');
            }
        })
        .catch(()=>{
            showToast('Đã có lỗi xảy ra', 'error');
        });
    });
});




