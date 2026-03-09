const addBtn = document.getElementById('openAddLink');
const addModal = document.getElementById('addModal');
const closeAdd = document.getElementById('closeAddModal');

addBtn?.addEventListener('click',()=> {
    addModal.classList.add('show');
    resetAddModal();
});
closeAdd?.addEventListener('click',()=> addModal.classList.remove('show'));

// Tabs
document.querySelectorAll('.add-tab-btn').forEach(btn=>{
  btn.onclick=()=>{
    const modal = document.querySelector('.login-modal');
    const tab = btn.dataset.tab;
    if (brandCount === 0) {
        alert("Please create at least one folder before adding links.");
        return;
    }
    document.querySelectorAll('.add-tab-btn').forEach(b=>b.classList.remove('active'));
    document.querySelectorAll('.add-tab-content').forEach(c=>c.classList.remove('show'));
    btn.classList.add('active');

    document.getElementById('tab-'+tab).classList.add('show');

    if(tab === 'link'){
      modal.classList.add('wide');
    } else {
      modal.classList.remove('wide');
    }
  }
});

// Add rows
document.getElementById('addMoreFolder').onclick=()=>{
  document.getElementById('folderList')
    .insertAdjacentHTML('beforeend','<div class="folder-row">'
        +'<input type="text" name="folder_name[]" placeholder="📁 Folder name..." required>'
        + '<button type="button" class="remove-folder">✕</button> </div>');
};

document.getElementById('folderList').addEventListener('click', function(e){
  if(e.target.classList.contains('remove-folder')){
    const rows = document.querySelectorAll('.folder-row');
    if (rows.length>1){
      e.target.closest('.folder-row').remove();
    }
  }
});

document.getElementById('addMoreLink').onclick = () => {
  const firstRow = document.querySelector('.link-row');
  const newRow = firstRow.cloneNode(true);

  // Clear values
  newRow.querySelector('input[name="link_name[]"]').value = '';
  newRow.querySelector('input[name="link_url[]"]').value = '';
  newRow.querySelector('select[name="folder_id[]"]').selectedIndex = 0;

  document.getElementById('linkList').appendChild(newRow);
};

document.getElementById('linkList').addEventListener('click', e => {
  if(e.target.classList.contains('remove-link')){
    const rows = document.querySelectorAll('.link-row');
    if(rows.length > 1){
      e.target.closest('.link-row').remove();
    }
  }
});

let draggedLinkId = null;

function handleDrag(ev) {
  draggedLinkId = ev.target.dataset.linkId;
}

function handleDrop(ev) {
  ev.preventDefault();
  const folderId = ev.currentTarget.dataset.folderId;

  fetch("/move_link", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken()
    },
    body: JSON.stringify({
      link_id: draggedLinkId,
      folder_id: folderId
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      location.reload();
    } else {
      alert("❌ Move failed");
    }
  });
}

function openLink(url) {
    window.open(url, '_blank');
}
function openAddLinkForFolder(folderId){

  const modal = document.getElementById('addModal');
  modal.classList.add('show');

  // Chuyển sang tab Link
  document.querySelectorAll('.add-tab-btn').forEach(b=>b.classList.remove('active'));
  document.querySelectorAll('.add-tab-content').forEach(c=>c.classList.remove('show'));

  document.querySelector('.add-tab-btn[data-tab="link"]').classList.add('active');
  document.getElementById('tab-link').classList.add('show');

  // Gán folder_id
  document.getElementById('folderIdHidden').value = folderId;

  // Ẩn select
  document.getElementById('folderSelect').style.display = 'none';
  document.getElementById('folderSelect').removeAttribute('required');
   document.querySelector('.add-tab-bar').style.display = 'none';
  // Đổi subtitle
  document.querySelector('.modal-sub').innerText = 'Add new links';
  // Modal wide
  document.querySelector('.login-modal').classList.add('wide');
};

function resetAddModal(){
  document.getElementById('folderSelect').style.display = 'flex'
  document.querySelector('.modal-sub').textContent = 'Create folders & add your links';
  document.querySelectorAll('.add-tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.add-tab-content').forEach(c => c.classList.remove('show'));
  document.querySelector('.add-tab-bar').style.display = 'flex';
  document.querySelector('.add-tab-btn[data-tab="folder"]').classList.add('active');
  document.getElementById('tab-folder').classList.add('show');
  const select = document.getElementById('folderSelect');
  if (select) select.style.display = '';
  select.setAttribute('required', 'required');

  // 5. Bỏ wide
  document.querySelector('.login-modal').classList.remove('wide');
  document.getElementById('folderIdHidden').value = '';
}

function startEditBrand(btn){
    const row = btn.closest('.brand-title-row');
    const NameEl = row.querySelector('.brand-name');
    brandId = row.dataset.brandId;
    const oldName = NameEl.textContent.trim();

    const input = document.createElement('input');
    input.type = 'text';
    input.value = oldName;
    input.className = 'brand-name-input';

    NameEl.replaceWith(input);
    input.focus();
    input.select();

    input.addEventListener('keydown',function(e) {
        if (e.key === 'Enter'){
            saveBrandName(brandId, input.value.trim());
        }
        if(e.key === 'Escape'){
            cancelEdit(input, oldName);
        }
    });

    input.addEventListener('blur', function(){
        saveBrandName(brandId, input.value.trim());
    });
}

function cancelEdit(input, oldName){
    const h2 = document.createElement('h2');
    h2.className = 'brand-name';
    h2.textContent = oldName;
    input.replaceWith(h2);
}

function saveBrandName(brandId, newname){
    if(!newname) return;

    fetch(`/brand/update/${brandId}`, {
        method: 'POST',
        headers:{
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        },
        body: JSON.stringify({name:newname})
    })
    .then(r => r.json())
    .then(data => {
        if(data.success){
            const input = document.querySelector('.brand-name-input');
            const h2 = document.createElement('h2');
            h2.className = 'brand-name';
            h2.textContent = newname;
            input.replaceWith(h2);
        }else{
            alert('Update failed');
        }
    });
}

function openEditLinkModal(btn){
    const folderId = btn.dataset.folderId;
    const linkId = btn.dataset.linkId;
    const linkName = btn.dataset.linkName;
    const linkUrl = btn.dataset.linkUrl;

    document.getElementById('edit_folder_id').value = folderId;
    document.getElementById('edit_link_id').value = linkId;
    document.getElementById('edit_link_name').value = linkName;
    document.getElementById('edit_link_url').value = linkUrl;

    document.getElementById('editLinkModal').style.display = 'flex';
}

function closeAddModalEditLink(){
    document.getElementById('editLinkModal').style.display = 'none';
}

