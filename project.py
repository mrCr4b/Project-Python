from flask import Flask, redirect, url_for, render_template, request, session
from sqlalchemy import Boolean, DateTime, Integer, LargeBinary
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'hello'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/proj_py'

db = SQLAlchemy(app)

class tai_khoan(db.Model):
    id_tai_khoan = db.Column(Integer, primary_key=True, nullable=False)
    ten_dang_nhap = db.Column(db.String(50), nullable=False)
    mat_khau = db.Column(db.String(50), nullable=False)
    phan_quyen = db.Column(Integer, nullable=False)
    khoa = db.Column(Integer, nullable=False)
    
        
class san_pham(db.Model):
    id_san_pham = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    gia_tien = db.Column(Integer, nullable=False)
    hinh_anh = db.Column(LargeBinary, nullable=False)
    
class gio_hang(db.Model):
    id_gio_hang = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_tai_khoan = db.Column(Integer, index=True, nullable=False)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    so_luong = db.Column(Integer, nullable=False)
    so_tien = db.Column(Integer, nullable=False)
    
class hoa_don(db.Model):
    id_hoa_don = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_tai_khoan = db.Column(Integer, index=True, nullable=False)
    ngay_tao = db.Column(DateTime, index=True, nullable=False)
    tong_tien = db.Column(Integer, nullable=False)
    
class chi_tiet_hoa_don(db.Model):
    id_chi_tiet_hoa_don = db.Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    id_hoa_don = db.Column(Integer, index=True, nullable=False)
    ten_san_pham = db.Column(db.String(50), nullable=False)
    so_luong = db.Column(Integer, nullable=False)
    so_tien = db.Column(Integer, nullable=False)
    

@app.route("/", methods = ['POST', 'GET'])
@app.route("/login", methods = ['POST', 'GET'])
def home():
    if request.method == "POST":
        username = request.form['user']
        password = request.form['pass']
        
        # Query the database to check if the username and password match
        check_admin = tai_khoan.query.filter_by(ten_dang_nhap=username, mat_khau=password, phan_quyen=1).first()
        check_user = tai_khoan.query.filter_by(ten_dang_nhap=username, mat_khau=password, phan_quyen=0, khoa=0).first()
        if check_admin:
            session['user'] = username
            session['id'] = check_admin.id_tai_khoan
            return redirect(url_for('admin'))
        if check_user:
            session['user'] = username
            session['id'] = check_user.id_tai_khoan
            return redirect(url_for('user'))
    return render_template("login.html")

@app.route("/register", methods = ['POST', 'GET'])
def register():
    return render_template("register.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/user")
def user():
    return render_template("user.html")

@app.route("/logout")
def logout():
    session.pop('user', None)
    #session.pop('id', None)
    return redirect(url_for('home'))

@app.route("/add_product", methods = ['POST', 'GET'])
def add_product():
    if request.method == "POST":
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        product_image = request.files['product_image'].read()
        
        # Create a new product object
        new_product = san_pham(ten_san_pham=product_name, gia_tien=product_price, hinh_anh=product_image)
        
        # Add the new product to the database session
        db.session.add(new_product)
        
        # Commit the transaction to save the changes to the database
        db.session.commit()
        
        # Redirect to a different page (e.g., the home page)
        return render_template("add_product.html")
    return render_template("add_product.html")

@app.route("/all_product_for_user", methods = ['POST', 'GET'])
def all_product_for_user():
    products = san_pham.query.all()
    return render_template('all_product_for_user.html', products=products)

@app.route("/all_product_for_admin", methods = ['POST', 'GET'])
def all_product_for_admin():
    products = san_pham.query.all()
    return render_template('all_product_for_admin.html', products=products)

@app.route("/add_to_cart", methods = ['POST', 'GET'])
def add_to_cart():
     if request.method == "POST":
        id_tai_khoan = session['id']
        ten_san_pham = request.form['ten_san_pham']
        so_luong = request.form['so_luong']
        gia_tien = request.form['gia_tien']
        
        new_cart = gio_hang(id_tai_khoan=id_tai_khoan, ten_san_pham=ten_san_pham, so_luong=so_luong, so_tien=int(so_luong)*int(gia_tien))
        # Add the new product to the database session
        db.session.add(new_cart)
        
        # Commit the transaction to save the changes to the database
        db.session.commit()
        
        # Redirect to a different page (e.g., the home page)
        return redirect(url_for('all_product_for_user'))
    
@app.route("/view_cart", methods = ['POST', 'GET'])
def view_cart():
    id_tai_khoan = session['id']
    products = gio_hang.query.filter_by(id_tai_khoan=id_tai_khoan)
    return render_template('cart.html', products=products)
    
@app.route("/pay", methods = ['POST', 'GET'])
def pay():
    tong_tien=0
    id_tai_khoan = session['id']
    products = gio_hang.query.filter_by(id_tai_khoan=id_tai_khoan)
    # Tính tổng tiền
    for product in products:
        tong_tien += product.so_tien
    # Thêm hóa đơn
    new_bill = hoa_don(id_tai_khoan=id_tai_khoan, ngay_tao=datetime.utcnow() + timedelta(hours=7), tong_tien=tong_tien)
    db.session.add(new_bill)
    db.session.commit()
    # Thêm chi tiết hóa đơn
    latest_bill = hoa_don.query.filter_by(id_tai_khoan=id_tai_khoan).order_by(hoa_don.id_hoa_don.desc()).first()
    id_hoa_don = latest_bill.id_hoa_don
    for product in products:
        ten_san_pham = product.ten_san_pham
        so_luong = product.so_luong
        so_tien = product.so_tien
        bill_detail = chi_tiet_hoa_don(id_hoa_don=id_hoa_don, ten_san_pham=ten_san_pham, so_luong=so_luong, so_tien=so_tien)
        db.session.add(bill_detail)
        db.session.commit()
        
    # Xóa dữ liệu trong giỏ hàng
    # Select the rows you want to delete
    rows_to_delete = gio_hang.query.filter_by(id_tai_khoan=id_tai_khoan)

    # Delete the selected rows
    rows_to_delete.delete()

    # Commit the changes to the database
    db.session.commit()
        
    return redirect(url_for('view_cart'))

@app.route("/no_pay", methods = ['POST', 'GET'])
def no_pay():
    id_tai_khoan = session['id']
    # Xóa dữ liệu trong giỏ hàng
    # Select the rows you want to delete
    rows_to_delete = gio_hang.query.filter_by(id_tai_khoan=id_tai_khoan)

    # Delete the selected rows
    rows_to_delete.delete()

    # Commit the changes to the database
    db.session.commit()
        
    return redirect(url_for('view_cart'))
    

if __name__ == "__main__":
    app.run(debug=True)