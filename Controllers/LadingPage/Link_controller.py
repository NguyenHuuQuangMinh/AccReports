from flask import Blueprint, render_template, request, session, flash, redirect, url_for, jsonify
from models.LandingPage.weblink_model import LinkModel
from models.LandingPage.weblink_user_model import LinkUserModel
from Controllers.decorators import login_required_link


link_bp = Blueprint('link', __name__)

@link_bp.route('/weblink')
@login_required_link
def weblink():
    model = LinkModel()
    model_user = LinkUserModel()
    keyword = request.args.get('keyword', '')
    tab = request.args.get('tab', 'public')
    folders = model_user.get_folders(session['user_id_link'])
    if tab == 'public':
        Link_perBrand = model.get_all_link_brand(keyword)
    else:
        Link_perBrand = model_user.get_all_link_folder(session['user_id_link'],keyword)
    all_brand = model.get_all_brand()
    brands = {}
    for r in Link_perBrand:
        brand_id = r.BrandID
        if brand_id not in brands:
            brands[brand_id] = {
                "id": brand_id,
                "name": r.BrandName,
                "logo": getattr(r, "LogoLink", "") or "",
                "color": getattr(r, "Color", "#4f46e5") or "#4f46e5",
                "link": [],
            }
        if r.LinkName and r.Url:
            brands[brand_id]["link"].append({
                "name":r.LinkName,
                "url":r.Url,
                "LinkId": getattr(r, "LinkId", "") or ""
            })
    brand_count = len(brands)
    return render_template('LandingPage/mainpage/Link.html',
                           brands=brands.values(),
                           brands_all = all_brand,
                           keyword=keyword,
                           tab=tab,
                           folders=folders,
                           brand_count=brand_count
                           )


@link_bp.route('/add_folder', methods=['POST'])
@login_required_link
def add_folder():
    model = LinkUserModel()
    folder_names = request.form.getlist('folder_name[]')
    for name in folder_names:
        if name.strip():
            add = model.insert_folder(name.strip(), session['user_id_link'])
            if add == 'EXIST':
                flash('❌ folder already exists', 'warning')
                return redirect(url_for('link.weblink'))
    flash("✅ Added folder(s) successfully", "success")
    return redirect(url_for('link.weblink', tab='your'))

@link_bp.route('/add_link', methods=['POST'])
@login_required_link
def add_link():
    model = LinkUserModel()
    link_names = request.form.getlist('link_name[]')
    link_urls = request.form.getlist('link_url[]')
    folder_ids = request.form.getlist('folder_id[]')
    folder_id_multi = request.form.get('folder_id_multi')
    if not folder_id_multi:
        for name, url, folder_id in zip(link_names, link_urls, folder_ids):
            if not name.strip() or not url.strip() or not folder_id:
                continue
            add = model.insert_link(
                user_id=session['user_id_link'],
                link_name=name.strip(),
                link_url=url.strip(),
                folder_id=folder_id
            )
            if add == 'EXIST':
                flash('❌ link already exists', 'warning')
                return redirect(url_for('link.weblink', tab='your'))
    else:
        for name, url in zip(link_names, link_urls):
            if not name.strip() or not url.strip():
                continue
            add = model.insert_link(
                user_id=session['user_id_link'],
                link_name=name.strip(),
                link_url=url.strip(),
                folder_id=folder_id_multi
            )
            if add == 'EXIST':
                flash('❌ link already exists', 'warning')
                return redirect(url_for('link.weblink', tab='your'))


    flash("✅ Added link(s) successfully", "success")
    return redirect(url_for('link.weblink', tab='your'))

@link_bp.route('/move_link', methods=['POST'])
@login_required_link
def move_link():
    data = request.get_json()
    link_id = data.get('link_id')
    folder_id = data.get('folder_id')

    if not link_id or not folder_id:
        return jsonify(success=False), 400
    model = LinkUserModel()
    model.update_link_folder(link_id, folder_id, session['user_id_link'])
    return jsonify(success=True)

@link_bp.route('/delete_link/<int:id_link>', methods=['POST'])
@login_required_link
def delete_link(id_link):
    user = session.get('user_id_link')
    model = LinkUserModel()
    delete = model.delete_link(id_link,user)
    if not delete:
        flash('❌ File not found', 'warning')
    else:
        flash("✅ Deleted link successfully", "success")
    return redirect(url_for('link.weblink', tab='your'))

@link_bp.route('/delete_folder/<int:id_folder>', methods=['POST'])
@login_required_link
def delete_folder(id_folder):
    user = session.get('user_id_link')
    model = LinkUserModel()
    delete = model.delete_folder(id_folder,user)
    if not delete:
        flash('❌ Folder not found', 'warning')
    else:
        flash("✅ Deleted folder and link(s) successfully", "success")
    return redirect(url_for('link.weblink', tab='your'))

@link_bp.route('/brand/update/<int:brand_Id>', methods=['POST'])
@login_required_link
def update_brand(brand_Id):
    model = LinkUserModel()
    data = request.get_json()
    newname = data.get('name', '').strip()
    if not newname:
        return jsonify(success=False), 400

    brand = model.update_brand(brand_Id,newname)
    if brand == 'EXIST':
        return jsonify(success=False), 400
    return jsonify(success=True)

@link_bp.route('/link/update/', methods=['POST'])
@login_required_link
def update_link():
    folder_id = request.form.get('folder_id')
    link_id = request.form.get('link_id')
    link_name = request.form.get('name')
    link_url = request.form.get('url')
    user_id = session.get('user_id_link')

    if not all([folder_id, link_id, link_name, link_url]):
        flash('Missing data', 'error')
        return redirect(url_for('link.weblink', tab='your'))

    models = LinkUserModel()
    update = models.update_link(user_id,folder_id,link_id,link_name,link_url)
    if update == 'EXIST':
        flash('Data does not exist', 'error')
        return redirect(url_for('link.weblink', tab='your'))

    flash('Updated link successful', 'success')
    return redirect(url_for('link.weblink', tab='your'))


