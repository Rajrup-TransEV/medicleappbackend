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
from controller.doctorsops.lessdoctor import lessdocbp
from controller.appoinmentops.appoinmenthistory import getappoinmenthistorybp
from controller.patientops.patientview import patientviewbp
from controller.doctorsops.getllprescribe import getallprescribebp
from controller.doctorsops.getprescribebyid import getprescribebyidbp
from controller.doctorsops.getprescrbbypatientid import getprescribebypatientidbp
from controller.doctorsops.getprescribbydoctorid import getprescribebydoctoridbp
from controller.facilitymanagement.faciltyopscreate import facilityopscreatebp
from controller.facilitymanagement.facilityopsgetall import facilityopsgetallbp
from controller.facilitymanagement.getfaciltydetailsbyid import getfacilitydetailsbyidbp
from controller.facilitymanagement.deletefacility import deletefacilitybp
from controller.facilitymanagement.facilityupdate import facilityupdatebp
from controller.management.wardmanagementcreate import wardmanagementcreatebp
from controller.management.roommanagementcreate import roommanagementcreatebp
from controller.management.getwarddetailsbyid import getwarddetailsbyidbp
from controller.management.getallward import getallwardbp
from controller.management.getallrooms import getallroomsbp
from controller.management.getroombyid import getroombyidbp
from controller.management.assignbedtopatient import assignbedtopatientbp
from controller.management.getbedetails import getbeddetailsbp
from controller.management.getallbeddetails import getallbeddetailsbp
from controller.management.equipmentmanagement.createequipment import createequipmentbp
from controller.management.equipmentmanagement.getallequipment import getallequipmentbp
from controller.management.equipmentmanagement.getequipmentbyid import getallequipmentbyidbp
from controller.management.equipmentmanagement.updateequipmentdetails import updateequipmentbp
from controller.management.equipmentmanagement.deleteequipment import deleteequipmentbp
from controller.staffmanagement.stafflistcreate import stafflistcreatebp
from controller.staffmanagement.stafflist import stafflistbp
from controller.staffmanagement.staffid import getstaffdetailsbyidbp
from controller.staffmanagement.staffupdate import staffupdatebp
from controller.staffmanagement.staffdelete import deletestaffxbp
from controller.management.patientadmitdetails import patientadmitdetailsbp
from controller.management.roomdelete import deleteroomdatabp
from controller.management.warddelete import deletewardbp
from controller.management.updatepatientadmit import updatepatientadmitxbp
from controller.labops.labtestdata import labtestdatabp
from controller.labops.labreportgetall import labreportgetallbp
from controller.labops.labreportgetbyid import labreportbyidbp
from controller.labops.labupdate import labupdatebp
from controller.labops.labdelete import labdeletebp
from controller.labops.labreportbypatinetid import labreportbypatientidbp
from controller.supportops.supportcreate import supportcreatebp
from controller.supportops.getsupportall import getsupportallbp
from controller.supportops.getsupportdetailsbyid import getsupportdetailsbyidbp
from controller.supportops.deletesupport import deletesupportdetailsbp
from controller.management.homecaremanagement.createhomecare import createhomecaremanagementbp
from controller.management.homecaremanagement.gethomecarebyid import gethomecarebyuidbp
from controller.management.homecaremanagement.updathomecare import updatehomecarebp
from controller.management.homecaremanagement.deletehomecare import deletehomecarebp
from dotenv import load_dotenv
from controller.faq.faqcreate import faqcreatebp
from controller.faq.faqgetall import faqgetallbp
from controller.faq.faqupdate import faqupdatebp
from controller.faq.faqdelete import faqdeletebp
from controller.survey.applicationsurvey.surveycreate import surveycreatebp
from controller.survey.applicationsurvey.getallsurveydata import getallsurveybp
from controller.survey.medicalsurvey.medicalsurveycreate import medicalsurveycreatebp
from controller.survey.medicalsurvey.getallms import getallmsbp
from controller.management.homecaremanagement.gethomecaredetbydocid import gethomecarebydocidbp
from controller.management.homecaremanagement.getdatabypatienceid import gethomecarebypatientidbp
from controller.management.homecaremanagement.getallhomecare import getallhomecarebp
from controller.management.homecaremanagement.cancelstatus import cancelstatusbp
from controller.guestlogin.guestlogin import guest_login_bp
from controller.billingmanagement.createbill import createbillbp
from controller.billingmanagement.updatebill import update_billbp
from controller.billingmanagement.getallbill import getallbillbp
from controller.billingmanagement.getbillbyemailid import getbillbypatientemailbp
from controller.billingmanagement.getbillbybillid import getbillbybillidbp
from controller.patientops.patientprofile.updateprescribeaccessupdate import prescribeaccessupdate_bp
from controller.patientops.patientprofile.updatelabdataaccess import labdataaccessupdate_bp
from controller.guestlogin.allguessaccessprescribedata import allguestaccessprescribedata_bp
from controller.guestlogin.allguestaccesslabdata import allguestaccesslabdata_bp
from controller.survey.applicationsurvey.deleteappsurvey import deleteappsurveybp
from controller.survey.medicalsurvey.deletemedicalsurvey import deletemedicalsurveybp
from controller.notify.notificationcreate import notifybp
from controller.notify.updatenotify import updatenotifybp
from controller.notify.deletenotify import deletenotifybp
from controller.notify.showactivenotify import showactivenotify_bp
from controller.notify.showallnotify import showallnotify_bp
from controller.notify.unseennotifyupdate import unseennotifyupdatebp
from controller.notify.showunseennotify import showunseennotify_bp


load_dotenv()

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
app.register_blueprint(patientviewbp)
app.register_blueprint(prescribeaccessupdate_bp)
app.register_blueprint(labdataaccessupdate_bp)
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
app.register_blueprint(lessdocbp)
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
app.register_blueprint(getappoinmenthistorybp)
app.register_blueprint(deleteapponbp)
#prescribe
app.register_blueprint(prescribe_bp)
app.register_blueprint(getallprescribebp)
app.register_blueprint(getprescribebyidbp)
app.register_blueprint(getprescribebypatientidbp)
app.register_blueprint(getprescribebydoctoridbp)
#facility create
app.register_blueprint(facilityopscreatebp)
app.register_blueprint(facilityopsgetallbp)
app.register_blueprint(getfacilitydetailsbyidbp)
app.register_blueprint(deletefacilitybp)
app.register_blueprint(facilityupdatebp)
#management operations
app.register_blueprint(wardmanagementcreatebp)
app.register_blueprint(roommanagementcreatebp)
app.register_blueprint(getroombyidbp)
app.register_blueprint(getallroomsbp)
app.register_blueprint(getallwardbp)
app.register_blueprint(getwarddetailsbyidbp)
app.register_blueprint(assignbedtopatientbp)
app.register_blueprint(getbeddetailsbp)
app.register_blueprint(getallbeddetailsbp)
app.register_blueprint(patientadmitdetailsbp)
app.register_blueprint(updatepatientadmitxbp)
#equipment management
app.register_blueprint(createequipmentbp)
app.register_blueprint(getallequipmentbp)
app.register_blueprint(getallequipmentbyidbp)
app.register_blueprint(updateequipmentbp)
app.register_blueprint(deleteequipmentbp)
#staff management
app.register_blueprint(stafflistcreatebp)
app.register_blueprint(stafflistbp)
app.register_blueprint(getstaffdetailsbyidbp)
app.register_blueprint(staffupdatebp)
app.register_blueprint(deletestaffxbp)
app.register_blueprint(deleteroomdatabp)
app.register_blueprint(deletewardbp)
#lab test data
app.register_blueprint(labtestdatabp)
app.register_blueprint(labreportgetallbp)
app.register_blueprint(labreportbyidbp)
app.register_blueprint(labupdatebp)
app.register_blueprint(labdeletebp)
app.register_blueprint(labreportbypatientidbp)
# SUPPORT OPS
app.register_blueprint(supportcreatebp)
app.register_blueprint(getsupportallbp)
app.register_blueprint(getsupportdetailsbyidbp)
app.register_blueprint(deletesupportdetailsbp)
#Home care management
app.register_blueprint(createhomecaremanagementbp)
app.register_blueprint(gethomecarebyuidbp)
app.register_blueprint(updatehomecarebp)
app.register_blueprint(gethomecarebydocidbp)
app.register_blueprint(gethomecarebypatientidbp)
app.register_blueprint(getallhomecarebp)
app.register_blueprint(cancelstatusbp)
app.register_blueprint(deletehomecarebp)
#faq create
app.register_blueprint(faqcreatebp)
app.register_blueprint(faqgetallbp)
app.register_blueprint(faqupdatebp)
app.register_blueprint(faqdeletebp)
#survey
app.register_blueprint(surveycreatebp)
app.register_blueprint(getallsurveybp)
app.register_blueprint(deleteappsurveybp)

#medical survey
app.register_blueprint(medicalsurveycreatebp)
app.register_blueprint(getallmsbp)
app.register_blueprint(deletemedicalsurveybp)
#guest login
app.register_blueprint(guest_login_bp)
app.register_blueprint(allguestaccessprescribedata_bp)
app.register_blueprint(allguestaccesslabdata_bp)
#billing
app.register_blueprint(createbillbp)
app.register_blueprint(update_billbp)
app.register_blueprint(getallbillbp)
app.register_blueprint(getbillbypatientemailbp)
app.register_blueprint(getbillbybillidbp)
#notify
app.register_blueprint(notifybp)
app.register_blueprint(updatenotifybp)
app.register_blueprint(deletenotifybp)
app.register_blueprint(showactivenotify_bp)
app.register_blueprint(showallnotify_bp)
app.register_blueprint(unseennotifyupdatebp)
app.register_blueprint(showunseennotify_bp)
#websocket based routes

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)  # Run the app with SocketIO support.