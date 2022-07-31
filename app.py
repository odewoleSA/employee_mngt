from flask import Flask, Blueprint, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import selectin_polymorphic

app = Flask(__name__)

app.secret_key = "hello"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///company_db.sqlite3' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class employee(db.Model):
	id = db.Column("id",db.Integer,primary_key=True)
	email = db.Column(db.String(100))
	fullname = db.Column(db.String(100))
	uname = db.Column(db.String(100))
	pswd = db.Column(db.String(100))
	department = db.Column(db.String(200))
	role = db.Column(db.String(100))

	def __init__(self,email,fullname,uname,pswd):
		self.email = email
		self.fullname = fullname
		self.uname = uname
		self.pswd = pswd

class department(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), unique=True)
	description = db.Column(db.String(200))

	def __init__(self,name,description):
		self.name = name
		self.description = description

class role(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(60), unique=True)
	description = db.Column(db.String(200))

	def __init__(self,name,description):
		self.name = name
		self.description = description

@app.route("/")
@app.route("/home")
def home():
	return render_template("index.html")

@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		email = request.form["email"]
		fullname = request.form["fullname"]
		uname = request.form["uname"]
		pswd = request.form["pswd"]
		cpswd = request.form["cpswd"]
		#checking if pswd matches
		if (pswd != cpswd):
			flash(f'Password does not Match','error')
			return redirect(url_for("register"))
		else:
			#checking DB if employee already registered
			found_user = employee.query.filter_by(email=email).all()
			found_user2 = employee.query.filter_by(uname=uname).all()

			if (found_user and found_user2):
				#if employee already exist
				flash(f'User Already Exist. Pls, Login!','info') 
				return redirect(url_for("register"))
			else:
				#adding new employee to DB
				employee_info = employee(email,fullname,uname,pswd)
				db.session.add(employee_info)
				db.session.commit()
				flash(f'You have successfully registered!','info')
				return redirect(url_for("register"))
	else:
		return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
	if request.method == "POST":
		email = request.form["email"]
		pswd = request.form["pswd"]

		found_user = employee.query.filter_by(email=email).first()
		if found_user:
			orig_pswd = found_user.pswd
			if orig_pswd == pswd:
				session.permanent = True
				session["user"] = found_user.uname
				user = session["user"]
				if "Admin" in session["user"]:
					# flash(f'Admin Login Successfully!','info')
					return redirect(url_for("admin"))
				else:
					return redirect(url_for("userPortal"))
			else:
				flash(f'Invalid Username/Password','info')
				return render_template("login.html")
		else:
			flash(f'User Not Registered!','info')
			return render_template("login.html")
	else:
		if "user" in session:
			if "Admin" in session["user"]:
				# flash(f'Admin Already Logged In!','info')
				return redirect(url_for("admin"))
			else:
				return redirect(url_for("userPortal"))
				
	return render_template("login.html")

@app.route("/userInfo")
def userPortal():
    if "user" in session:
        user = session["user"]
        user_details = employee.query.filter_by(uname=user).first()

        fname = user_details.fullname
        uemail = user_details.email
        funame = user_details.uname
        user_info = {'Full Name':fname, 'Email':uemail, 'Username':funame}
        return render_template("employee_portal.html",user=user, myinfo=user_info)
    else:
        flash(f'You are not logged in!','error')
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    if "user" in session:
        user = session["user"]
        flash(f'You have been logged out, {user}','info')
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			return render_template("dashboard.html",user=user)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		return render_template("errors/403.html")
		# flash(f'You are not logged in!','error')
		# return redirect(url_for("forbidden"))

@app.route("/admin/employee")
def employees():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			return render_template("employee.html",user=user, employees=employee.query.all())
			# return render_template("employee.html")
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/department")
def departments():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			return render_template("department.html",user=user, departments=department.query.all())
			# return render_template("department.html")
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/role")
def roles():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			return render_template("role.html",user=user, roles=role.query.all())
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/department/add_department", methods=["POST", "GET"])
def addDepartment():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			if request.method == "POST":
				name = request.form["name"]
				description = request.form["description"]
				#checking DB if department already added
				found_dept = department.query.filter_by(name=name).all()
				if (found_dept):
					#if department already exist
					flash(f'Department Already Added!','info') 
					return render_template("add_department.html",user=user)
				else:
					#adding new department to DB
					department_info = department(name,description)
					db.session.add(department_info)
					db.session.commit()
					flash(f'Department Added Successfully!','info')
					return render_template("department.html",user=user,departments=department.query.all())
			else:
				return render_template("add_department.html",user=user)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/department/edit/<string:name>", methods=["POST", "GET"])
def editDepartment(name):
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			record_obj = db.session.query(department).filter(department.name==name).first()
			nameVal = record_obj.name
			descriptionVal = record_obj.description
			return render_template("edit_department.html",user=user,name=nameVal,description=descriptionVal)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/department/update", methods=["POST", "GET"])
def departmentUpdate():
    if "user" in session:
        if "Admin" in session["user"]:
            if request.method == "POST":
                name = request.form["name"]
                description = request.form["description"]
                # Updating Data
                rows_updated = department.query.filter_by(name=name).first()
                rows_updated.name = name
                rows_updated.description = description
                db.session.commit()
                flash(f'Department Updated Successfully!','info')
                return redirect(url_for("departments"))
            else:
                return redirect(url_for("departmentUpdate"))
        else:
            flash(f'Permission Denied!','error')
            return redirect(url_for("login"))
    else:
        flash(f'You are not logged in!','error')
        return redirect(url_for("login"))

@app.route("/admin/department/delete/<string:name>")
def deleteDepartment(name):
    if "user" in session:
        if "Admin" in session["user"]:
            record_obj = db.session.query(department).filter(department.name==name).first()
            db.session.delete(record_obj)
            db.session.commit()
            flash(f'Department Deleted Successfully!','info')
            return redirect(url_for("departments"))
        else:
            flash(f'Permission Denied!','error')
            return redirect(url_for("login"))
    else:
        flash(f'You are not logged in!','error')
        return redirect(url_for("login"))

@app.route("/admin/role/add_role", methods=["POST", "GET"])
def addRole():
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			if request.method == "POST":
				name = request.form["name"]
				description = request.form["description"]
				#checking DB if role already added
				found_role = role.query.filter_by(name=name).all()
				if (found_role):
					#if role already exist
					flash(f'Error: role name already exists.','info') 
					return render_template("add_role.html",user=user)
				else:
					#adding new department to DB
					role_info = role(name,description)
					db.session.add(role_info)
					db.session.commit()
					flash(f'You have successfully added a new role.','info')
					return render_template("role.html",user=user,roles=role.query.all())
			else:
				return render_template("add_role.html",user=user)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/role/edit/<string:name>", methods=["POST", "GET"])
def editRole(name):
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			record_obj = db.session.query(department).filter(department.name==name).first()
			nameVal = record_obj.name
			descriptionVal = record_obj.description
			return render_template("edit_role.html",user=user,name=nameVal,description=descriptionVal)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/role/update", methods=["POST", "GET"])
def roleUpdate():
    if "user" in session:
        if "Admin" in session["user"]:
            if request.method == "POST":
                name = request.form["name"]
                description = request.form["description"]
                # Updating Data
                rows_updated = role.query.filter_by(name=name).first()
                rows_updated.name = name
                rows_updated.description = description
                db.session.commit()
                flash(f'Role Updated Successfully!','info')
                return redirect(url_for("roles"))
            else:
                return redirect(url_for("roleUpdate"))
        else:
            flash(f'Permission Denied!','error')
            return redirect(url_for("login"))
    else:
        flash(f'You are not logged in!','error')
        return redirect(url_for("login"))

@app.route("/admin/role/delete/<string:name>")
def deleteRole(name):
    if "user" in session:
        if "Admin" in session["user"]:
            record_obj = db.session.query(role).filter(role.name==name).first()
            db.session.delete(record_obj)
            db.session.commit()
            flash(f'Role Deleted Successfully!','info')
            return redirect(url_for("roles"))
        else:
            flash(f'Permission Denied!','error')
            return redirect(url_for("login"))
    else:
        flash(f'You are not logged in!','error')
        return redirect(url_for("login"))

@app.route("/admin/department/assign/<string:name>")
def AssignEmployee(name):
	if "user" in session:
		if "Admin" in session["user"]:
			user = session["user"]
			record_obj = db.session.query(employee).filter(employee.uname==name).first()
			fnameVal = record_obj.fullname
			unameVal = record_obj.uname
			# get department name
			obj_dept_name = db.session.query(department).all()
			# get role name
			obj_role_name = db.session.query(role).all()
			if ('Admin' in unameVal):
				flash(f'Admin cannot be assigned!','error')
				return redirect(url_for("employees"))
			else:
				return render_template("assign_employee.html",user=user,uname=unameVal,fname=fnameVal,dept_name=obj_dept_name,role_name=obj_role_name)
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))

@app.route("/admin/employee/assign", methods=["POST", "GET"])
def DeptRoleAssign():
	if "user" in session:
		if "Admin" in session["user"]:
			if request.method == "POST":
				uname = request.form["uname"]
				deptname = request.form["department"]
				rolename = request.form["role"]
				# Assign Dept and Role to Employee
				rows_updated = employee.query.filter_by(uname=uname).first()
				rows_updated.department = deptname
				rows_updated.role = rolename
				db.session.commit()
				flash(f'You have successfully assigned a department and role','info')
				return redirect(url_for("employees"))
			else:
				return redirect(url_for("DeptRoleAssign"))
		else:
			flash(f'Permission Denied!','error')
			return redirect(url_for("login"))
	else:
		flash(f'You are not logged in!','error')
		return redirect(url_for("login"))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)