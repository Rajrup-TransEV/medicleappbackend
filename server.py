# import eventlet
# eventlet.monkey_patch()

from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO,emit
#
from controller.patientops.signup import signup_bp
from controller.patientops.login import login_bp
from controller.adminops.login import admin_login_bp
from controller.adminops.signup import admin_signup_bp
from controller.superadminops.login import super_admin_login_bp
from controller.superadminops.signup import super_admin_signup_bp
from controller.superadminops.suforgotpassword import superadminpasswordreset_bp
from controller.adminops.adforgotpassword import adminpasswordreset_bp
from controller.patientops.pforgotpassword import patientpasswordreset_bp
from controller.patientops.patientprofile.pprofilecreate import pprofilecreate_bp
from controller.patientops.patientprofile.getprofilebyid import getprofiebyid_bp
from controller.patientops.patientprofile.getallpatient import getallpatient_bp
from controller.patientops.patientprofile.deleteprofile import deleteprofile_bp
from controller.doctorsops.doctorsignup import doctorsignup_bp
from controller.doctorsops.login import doctor_login_bp
from controller.doctorsops.getdoctordetailsbyid import getdoctordetailsbyid_bp
from controller.doctorsops.getalldoctor import getalldoctor_bp
from controller.doctorsops.doctbyspecialization import getdoctorbyspc_bp
from controller.doctorsops.doctorleave import doctorleave_bp
from controller.doctorsops.doctorleaveupdate import doctorleaveupdate_bp
from controller.doctorsops.deleteleave import deleteleave_bp
from controller.doctorsops.getallleave import getallleave_bp
from controller.doctorsops.doctorpasswordreset import doctorpasswordreset_bp
from controller.doctorsops.updatedoctordata import updatedoctordata_bp
from controller.doctorsops.deletedoctor import deletedoctor_bp
from controller.adminops.getbyidadmin import getadminbyidbp
from controller.doctorsops.getallleavebydocid import getallleavebydocidbp
from controller.appoinmentops.createappoinmentdetails import createappoinment_bp
from controller.appoinmentops.getappoinmentdetails import getappoinmentdetailsbp
from controller.appoinmentops.getallappoinmentdetails import getallappoinmentbp
from controller.appoinmentops.updateappoinmentops import updateappoinmentopsbp
from controller.appoinmentops.deleteappn import deleteapponbp
from controller.doctorsops.prescribe import prescribe_bp
from controller.adminops.deleteaccount import deleteadminaccountbp

app = Flask(__name__)

CORS(app, resources={r"/*": {
    "origins": "*",  # Change '*' to specific origins in production
    "allow_headers": ["Content-Type", "Authorization"],
    "methods": ["GET", "POST", "OPTIONS"]
}})

# Initialize the Limiter
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["20000 per day", "5000 per hour"]  # Adjust limits as needed
)

socketio = SocketIO(app, cors_allowed_origins="*")



@app.route("/", methods=['GET'])
def index():
    return jsonify({"message": "App access not allowed"})


#blueprint rest apis
#auth routes
app.register_blueprint(signup_bp) #/patients/signup
app.register_blueprint(login_bp) #/patients/login
app.register_blueprint(admin_login_bp) #/admin/login
app.register_blueprint(admin_signup_bp) #/admin/signup
app.register_blueprint(super_admin_login_bp) #/superadmin/login
app.register_blueprint(super_admin_signup_bp) #/superadmin/signup
app.register_blueprint(superadminpasswordreset_bp) #/superadminpasswordreset
app.register_blueprint(adminpasswordreset_bp) #/adminpasswordreset
app.register_blueprint(patientpasswordreset_bp)#/patientpasswordreset
#auth route ends
#patient profile routes
app.register_blueprint(pprofilecreate_bp) #/patients/profile/update
app.register_blueprint(getprofiebyid_bp) #/patients/profile/getbyid
app.register_blueprint(getallpatient_bp) #/patientops/getallpatient
app.register_blueprint(deleteprofile_bp) #/patientops/deleteprofile
#patient profile route ends
#doctor routes
app.register_blueprint(doctorsignup_bp) #/doctor/signup
app.register_blueprint(doctor_login_bp) #/doctors/login
app.register_blueprint(getdoctordetailsbyid_bp) #/doctors/getbyid
app.register_blueprint(getalldoctor_bp)#/doctorops/getalldoctor
app.register_blueprint(getdoctorbyspc_bp)#/doctors/getdoctorbyspc
app.register_blueprint(doctorleave_bp)#/doctors/leave
app.register_blueprint(doctorleaveupdate_bp) #/doctors/leave
app.register_blueprint(deleteleave_bp) #/doctorsops/deleteleave
app.register_blueprint(getallleave_bp) #/doctorops/getallleave
app.register_blueprint(doctorpasswordreset_bp) #/doctorpasswordreset
app.register_blueprint(updatedoctordata_bp) #/doctors/profile/update
app.register_blueprint(deletedoctor_bp) #/doctorsops/deletedoctor
app.register_blueprint(getallleavebydocidbp)#'/doctors/leave
#doctor route ends
#admin routes
app.register_blueprint(deleteadminaccountbp)
app.register_blueprint(getadminbyidbp)
#end admin
#create appoinments
app.register_blueprint(createappoinment_bp)
app.register_blueprint(getappoinmentdetailsbp)
app.register_blueprint(getallappoinmentbp)
app.register_blueprint(updateappoinmentopsbp)
app.register_blueprint(deleteapponbp)
#prescribe
app.register_blueprint(prescribe_bp)

#websocket based routes

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run the app with SocketIO support.