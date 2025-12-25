function showToast(message, category = "error") {
    const overlay = document.createElement("div");
    overlay.className = "toast-overlay";
    overlay.innerHTML = `<div class="toast ${category}">${message}</div>`;
    document.body.appendChild(overlay);
    setTimeout(() => overlay.remove(), 4000);
}

document.addEventListener("click", async function (e) {
    const btn = e.target.closest(".download");
    if (!btn) return;

    const reportId = btn.dataset.reportId;

    const res = await fetch(`/download/prepare/${reportId}`);
    const data = await res.json();
    if (data.error) {
        showToast(data.message);
        return;
    }
    if (data.need_params) {
        openParamModal(reportId, data.params);
    } else {
        window.location.href = data.download_url;
    }
});

function openParamModal(reportId, params) {
    const modal = document.getElementById("param-modal");
    const fields = document.getElementById("param-fields");
    const form = document.getElementById("param-form");

    fields.innerHTML = "";

    params.forEach(p => {
        const safeName = p.name.replace(/\s+/g, '_');

        fields.innerHTML += `
            <div class="form-group">
                <label for="param_${safeName}">
                    ${p.name}
                </label>
                <input type="text"
                       id="param_${safeName}"
                       name="param_${p.name}"
                       placeholder="Nhập ${p.name}"
                       required>
            </div>
        `;
    });

    form.onsubmit = function (e) {
        e.preventDefault();

        const formData = new FormData(form);

        fetch(`/download/confirm/${reportId}`, {
            method: "POST",
            body: formData
        }).then(async response => {
            const blob = await response.blob();

            // 👉 LẤY TÊN FILE TỪ HEADER
            let filename = "report.xls";
            const disposition = response.headers.get("Content-Disposition");

            if (disposition && disposition.includes("filename=")) {
                filename = disposition
                    .split("filename=")[1]
                    .replace(/"/g, "")
                    .trim();
            }

            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");

            a.href = url;
            a.download = filename;

            document.body.appendChild(a);
            a.click();

            a.remove();
            window.URL.revokeObjectURL(url);

            closeModal();
        });
    };

    modal.classList.remove("hidden");
}

function closeModal() {
    document.getElementById("param-modal").classList.add("hidden");
}