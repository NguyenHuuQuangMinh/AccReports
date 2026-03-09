from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models.LandingPage.authenticate import AuthenticLinkModel
from Controllers.extensions import limiter

auth_bp = Blueprint('auth', __name__)
@auth_bp.route('/')
def index():
    # CHƯA đăng nhập → login
    if 'user_id_link' not in session:
        return redirect(url_for('auth.login'))

    return redirect(url_for('link.weblink'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id_link' in session:
        return redirect(url_for('link.weblink'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')
        models = AuthenticLinkModel()
        user = models.authetic(username, password)
        if not username or not password:
            flash("❌ Vui lòng nhập đầy đủ tài khoản và mật khẩu", "error")
            return redirect(url_for('auth.login'))
        if user and int(user.status) == 0:
            flash("🚫 Tài khoản của bạn đã bị khóa!", 'error')
            return redirect(url_for('auth.login'))
        if user and int(user.roleStatus) == 0:
            flash("🚫 Quyền hạn của bạn đã bị khóa!", 'error')
            return redirect(url_for('auth.login'))
        if not user:
            flash('❌ Sai tên đăng nhập hoặc mật khẩu', 'error')
            return redirect(url_for('auth.login'))
        else:
            session.clear()
            session['user_id_link'] = user.id
            session['username_link'] = user.username
            name = user.full_name.strip().split()[-1]
            session['name'] = name
            if remember:
                session.permanent = True
            else:
                session.permanent = False
            flash(f'✅ Đăng nhập thành công, mừng quay trở lại {name}', 'success')
            return redirect(url_for('link.weblink'))
    return render_template('LandingPage/auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

# @auth_bp.route('/change-password', methods=['POST'])
# @limiter.limit("5 per minute")
# def change_password():
#     if 'user_id_link' not in session:
#         return jsonify({'ok': False, 'message': 'Bạn chưa đăng nhập'}), 401
#
#     old_password = request.form.get('old_password')
#     new_password = request.form.get('new_password')
#     confirm_password = request.form.get('confirm_password')
#
#     models = AuthenticLinkModel()
#     user = models.get_by_id(session['user_id_link'])
#
#     if not UserModel.verify_password(old_password, user.passwordHash):
#         return jsonify({'ok': False, 'message': '❌ Mật khẩu cũ không đúng'})
#
#     if UserModel.verify_password(new_password, user.passwordHash):
#         return jsonify({'ok': False, 'message': '❌ Mật khẩu mới không được trùng mật khẩu cũ'})
#
#     if new_password != confirm_password:
#         return jsonify({'ok': False, 'message': '❌ Mật khẩu nhập lại không khớp'})
#
#     models.update_password(user.Id, new_password)
#
#     return jsonify({'ok': True, 'message': '✅ Đổi mật khẩu thành công'})
