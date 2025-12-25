from flask import Blueprint, render_template, flash, redirect, url_for,Response,request,session,jsonify
from Controllers.decorators import login_required
from models.Report_model import ReportModel
from models.Favourite_model import FavoriteModel
from models.User_model import UserModel
from requests_ntlm import HttpNtlmAuth
from collections import defaultdict
import requests
import os

user_bp = Blueprint('user', __name__)

@user_bp.route('/home')
@login_required
def home():
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'asc')
    reports = ReportModel.get_reports(keyword,1, sort)
    total_report = len(reports)
    favorites = FavoriteModel.get_user_favorites(session['user_id'])
    return render_template('user/home.html',
                           reports=reports,
                           total_reports=total_report,
                           keyword=keyword,
                           sort=sort,
                           favorites=favorites)

@user_bp.route('/download/prepare/<int:report_id>')
@login_required
def prepare_download(report_id):
    report = ReportModel.get_by_id(report_id)
    if not report:
        return jsonify({
            "error": True,
            "message": "Report không tồn tại"
        }), 404

    if not report["DownloadLink"]:
        return jsonify({
            "error": True,
            "message": "Report chưa được gán link download"
        }), 400

    # Tìm param rỗng
    empty_params = [
        p for p in report["Params"]
        if p["value"] is None or str(p["value"]).strip() == ""
    ]

    if empty_params:
        return jsonify({
            "need_params": True,
            "report_id": report_id,
            "params": empty_params
        })

    return jsonify({
        "need_params": False,
        "download_url": url_for('user.download_report', report_id=report_id)
    })

@user_bp.route('/download/confirm/<int:report_id>', methods=['POST'])
@login_required
def confirm_download(report_id):
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)

    if not report:
        flash('Report không tồn tại', 'error')
        return redirect(url_for('user.home'))

    override_params = {}

    for p in report["Params"]:
        key = f"param_{p['name']}"
        if key in request.form:
            override_params[p['name']] = request.form[key]

    # Build link với param user nhập
    download_url = ReportModel.build_download_link(report, override_params)

    UserModel.log_history(user_id, report_id, 'download')

    auth = HttpNtlmAuth(
        os.getenv('SSRS_USER'),
        os.getenv('SSRS_PASSWORD')
    )

    r = requests.get(download_url, auth=auth, stream=True)

    return Response(
        r.iter_content(8192),
        headers={
            "Content-Disposition": f'attachment; filename="{report["ReportName"]}.xls"',
            "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
        }
    )


@user_bp.route('/download/<int:report_id>')
@login_required
def download_report(report_id):
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))
    UserModel.log_history(user_id,report_id,'download')

    # Đường dẫn file thật (UNC hoặc local)
    file_path = ReportModel.build_download_link(report)   # ví dụ: \\SERVER\Reports\a.pdf
    print(file_path)
    auth = HttpNtlmAuth(
        os.getenv('SSRS_USER'),  # DOMAIN\\user
        os.getenv('SSRS_PASSWORD')
    )

    r = requests.get(
        file_path,
        auth=auth,
        stream=True
    )
    return Response(
        r.iter_content(8192),
        headers={
            "Content-Disposition": f'attachment; filename="{report["ReportName"]}.xls"',
            "Content-Type": r.headers.get("Content-Type", "application/octet-stream")
        }
    )

@user_bp.route('/report/<int:report_id>/view')
@login_required
def view_report(report_id):
    # Lấy thông tin report từ database
    user_id = session['user_id']
    report = ReportModel.get_by_id(report_id)
    if not report:
        flash('Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))

    file_url = report.FilePath

    if not file_url:
        flash('Link Report không tồn tại !!!', 'error')
        return redirect(url_for('user.home'))
    UserModel.log_history(user_id, report_id, 'view')
    # Trả file về client
    return redirect(file_url)

@user_bp.route('/favorite/<int:report_id>', methods=['POST'])
@login_required
def toggle_favorite(report_id):
    user_id = session['user_id']
    liked = FavoriteModel.toggle(user_id, report_id)

    return jsonify({'liked': liked})

@user_bp.route('/favorites')
@login_required
def favorites():
    user_id = session['user_id']

    # Lấy danh sách report đã favorite
    favorite_ids = FavoriteModel.get_user_favorites(user_id)
    keyword = request.args.get('keyword', '')
    sort = request.args.get('sort', 'asc')
    reports = ReportModel.get_reports_by_ids(favorite_ids,keyword,sort)
    total_report = len(reports)
    return render_template('user/favorites.html',
                           reports=reports,
                           total_reports=total_report,
                           keyword=keyword,
                           sort=sort)

@user_bp.route('/history')
@login_required
def history():
    user_id = session['user_id']
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    keyword = request.args.get('keyword', '').strip()
    histories = UserModel.download_history(user_id,from_date,to_date,keyword)
    histories_by_date = defaultdict(list)

    for r in histories:
        date_key = r.CreatedAt.strftime('%d/%m/%Y')
        histories_by_date[date_key].append(r)
    return render_template('user/history.html',
                                            histories_by_date=histories_by_date,
                                            from_date=from_date,
                                            to_date=to_date,
                                            keyword=keyword
                                            )




