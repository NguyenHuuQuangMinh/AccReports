function showToast(message, category = "error") {
    const overlay = document.createElement("div");
    overlay.className = "toast-overlay";
    overlay.innerHTML = `<div class="toast ${category}">${message}</div>`;
    document.body.appendChild(overlay);
    setTimeout(() => overlay.remove(), 4000);
}

function showLoading() {
  document.getElementById("loading-backdrop").style.display = "block";
  document.getElementById("loading-overlay").style.display = "block";
}

function hideLoading() {
  document.getElementById("loading-backdrop").style.display = "none";
  document.getElementById("loading-overlay").style.display = "none";
}
document.addEventListener("click", async function (e) {
    const btn = e.target.closest(".download");
    if (!btn) return;

    const reportId = btn.dataset.reportId;

    // 👉 HIỆN LOADING NGAY KHI CLICK
    showLoading();

    try {
        const res = await fetch(`/download/prepare/${reportId}`);
        const data = await res.json();

        if (data.error) {
            showToast(data.message);
            hideLoading()
            return;
        }

        if (data.need_params) {
            hideLoading()
            openParamModal(reportId, data.params);
        } else {
            // 👉 bắt đầu download
            window.location.href = data.download_url;
            setTimeout(() => {
                hideLoading()
            }, 800);
        }

    } catch (err) {
        showToast("Có lỗi khi chuẩn bị báo cáo!");
        hideLoading()
    }
});


function openParamModal(reportId, params) {
    const modal = document.getElementById("param-modal");
    const fields = document.getElementById("param-fields");
    const form = document.getElementById("param-form");

    fields.innerHTML = "";

    params.forEach(p => {
        const safeName = p.name.replace(/\s+/g, '_');
        const showNull = p.allow_null == 1;
        const showAll = p.allow_all == 1;
        let inputType = "text";
        let step = "";
        let placeholder = p.label || `Nhập ${p.name}`;
        let min = "";
        switch (p.datatype) {
            case "int":
                inputType = "number";
                step = "1";
                placeholder = p.label || "Chỉ nhập số nguyên";
                min = "0";
                break;

            case "decimal":
                inputType = "number";
                step = "any";
                placeholder = p.label || "Nhập số thập phân";
                min = "0";
                break;

            case "date":
                inputType = "date";
                placeholder = p.label || "Chọn ngày";
                break;

            case "datetime":
                inputType = "datetime-local";
                placeholder = p.label || "Chọn ngày & giờ";
                break;
        }
        fields.innerHTML += `
            <div class="form-group">
                <label for="param_${safeName}">
                    ${p.name}
                </label>
                <div class="param-input-row">
                    <input type="${inputType}"
                           id="param_${safeName}"
                           name="param_${p.name}"
                           ${step ? `step="${step}"` : ""}
                           ${min ? `min="${min}"`  : ""}
                           placeholder="${placeholder}"
                           >
                    ${showNull ? `
                            <label class="param-check">
                                <input type="checkbox"
                                       class="null-check"
                                       data-target="param_${safeName}"
                                       name="null_${p.name}"
                                       value="1">
                                Null
                            </label>
                        ` : ""}

                        ${showAll ? `
                            <label class="param-check">
                                <input type="checkbox"
                                       class="all-check"
                                       data-target="param_${safeName}"
                                       name="all_${p.name}"
                                       value="1">
                                All
                            </label>
                        ` : ""}
                </div>
            </div>
        `;
    });

    setTimeout(() => {

        document.querySelectorAll('.null-check, .all-check').forEach(cb => {

            cb.addEventListener('change', function () {

                const input = document.getElementById(this.dataset.target);

                if (this.checked) {
                    input.value = "";
                    input.disabled = true;
                } else {
                    input.disabled = false;
                }

            });

        });

    }, 0);

    form.onsubmit = async function (e) {
    e.preventDefault();

    // 👉 HIỆN LOADING
    showLoading();
    document.querySelectorAll('.null-check, .all-check').forEach(cb => {

        if (!cb.checked) {

            const hidden = document.createElement("input");

            hidden.type = "hidden";
            hidden.name = cb.name;
            hidden.value = "0";

            form.appendChild(hidden);
        }

    });
    const formData = new FormData(form);

    try {
        const response = await fetch(`/download/confirm/${reportId}`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken()
            },
            body: formData
        });

        const blob = await response.blob();

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

        closeModalReport();

    } catch (err) {
        showToast("Có lỗi khi tải báo cáo!");
    } finally {
        // 👉 TẮT LOADING
        hideLoading()
    }
};
    modal.classList.remove("hidden");
}

function closeModalReport() {
    document.getElementById("param-modal").classList.add("hidden");
}