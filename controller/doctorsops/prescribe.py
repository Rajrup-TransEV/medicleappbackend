import uuid
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from utils.logs import generatelogs
from reportlab.lib.pagesizes import A4  # Change to A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import textwrap

UPLOAD_FOLDER = 'uploads/medicaldirectory/prescribe/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    try:
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client[os.getenv('DB_NAME')]
        return db
    except PyMongoError as e:
        messagetype = 'error'
        message = f"Database connection error: {str(e)}"
        filelocation = 'patientops/login.py'
        generatelogs(messagetype, message, filelocation)
        raise

def wrap_text(pdf_canvas, text, max_width):
    """Wraps text to fit within a specified width."""
    wrapped_lines = []
    # Wrap text to 100 characters initially
    initial_wrap = textwrap.wrap(text, width=95)

    for line in initial_wrap:
        # Further wrap based on canvas width
        while pdf_canvas.stringWidth(line, 'Helvetica', 12) > max_width:
            # Split the line at the last space within max_width
            split_index = max_width // 6  # Rough estimate of average character width
            while split_index > 0 and line[split_index] != ' ':
                split_index -= 1
            
            if split_index == 0:  # No spaces found; break at max width
                split_index = len(line)

            wrapped_lines.append(line[:split_index])
            line = line[split_index:].lstrip()  # Remove leading space for next line

        if line:  # Add any remaining part of the line
            wrapped_lines.append(line)

    return wrapped_lines

prescribe_bp = Blueprint('prescribe_bp', __name__)

@prescribe_bp.route('/createprescription', methods=['POST'])
def createprescribfn():
    try:
        # Retrieve form data
        hospitalname = str(request.form.get('hospitalname'))
        doctorid = str(request.form.get('doctorid'))
        patientid = str(request.form.get('patientid'))
        dateandtime = "Tuesday, January 07, 2025, 3 PM IST"  # Updated date and time
        diagonistics = str(request.form.get('diagonistics'))

        # Save the file path to MongoDB
        db = get_db_connection()
        prescribe_collection = db['prescribe']
        doctor_collection = db['doctors']
        doctor = doctor_collection.find_one({"uid": doctorid})
        
        doctorfullname = doctor['fullname']
        docqualification = doctor['qualification']
        docspecialization = doctor['specialization']
        
        patientcollection = db['patients']
        patients = patientcollection.find_one({"uid": patientid})
        
        patientfirstname = patients['firstname']
        patientlastname = patients['lastname']

        # Generate a unique filename and save path
        unique_filename = f"prescription_{uuid.uuid4().hex}.pdf"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        # Generate PDF dynamically with A4 size
        pdf = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        # Header Section with a modern look
        pdf.setFillColor(HexColor("#4A90E2"))  # Blue header background
        pdf.rect(0, height - 120, width, 120, fill=1)

        # Hospital Logo (left side)
        pdf.drawImage('./static/logo.jpg', 20, height - 100, width=80, height=80)  # Adjust path and size as needed

        # Hospital Name (centered in header)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColor(HexColor("#FFFFFF"))  # White text
        pdf.drawCentredString(width / 2, height - 70, hospitalname)

        # Doctor Details Section below header
        pdf.setFont("Helvetica", 14)
        pdf.setFillColor(HexColor("#333333"))  # Dark text color

        pdf.drawString(20, height - 150, f"Doctor: {doctorfullname}")
        pdf.drawString(20, height - 170, f"Qualification: {docqualification}")
        pdf.drawString(20, height - 190, f"Specialization: {docspecialization}")

        # Patient Details Section
        pdf.setFont("Helvetica-Bold", 16)
        
        # Centered Patient Details Title
        pdf.drawString(20 ,height -220 , "Patient Details:")

        pdf.setFont("Helvetica",14)
        pdf.drawString(20 ,height -240 , f"Name: {patientfirstname} {patientlastname}")

        # Diagnostics Section
        pdf.setFont("Helvetica-Bold",16)
        
        diagnostics_title = "Diagnostics:"
        title_width = pdf.stringWidth(diagnostics_title, "Helvetica-Bold", 16)
        
        # Centered title for diagnostics section
        pdf.drawString((width - title_width) / 2, height - 260, diagnostics_title)  

        pdf.setFont("Helvetica",12)

        # Wrap diagnostics text to fit within the page width (100 characters per line)
        diagnostics_lines = wrap_text(pdf, diagonistics,max_width=width-40)
        
        for i,line in enumerate(diagnostics_lines):
            line_width = pdf.stringWidth(line, "Helvetica", 12)
            # Center each line of diagnostics text
            pdf.drawString((width - line_width) / 2, height - (280 + i *15),line)  

        # Date Section (Top Right) - Adjusted position to avoid cutting off
        pdf.setFont("Helvetica",12)
        
        pdf.drawString(width -180 ,height -40 ,f"Date: {dateandtime}")

        # Footer Section with a modern look
        pdf.setFillColor(HexColor("#E94E77"))   # Footer background color
        pdf.rect(0 ,0 ,width ,0.75 * inch ,fill=1)

        pdf.setFillColor(HexColor("#FFFFFF"))   # White text in footer
        pdf.setFont("Helvetica",10)

        pdf.drawString(20 ,0.25 * inch ,f"© {hospitalname}")

         # Add timestamp on right side of footer
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.drawString(width -180 ,0.25 * inch ,f"Generated on: {timestamp}")

         # Save the PDF
        pdf.save()

        prescribe_data = {
             "hospitalname": hospitalname,
             "patientfullname": patientfirstname + ' ' + patientlastname,
             "dateandtime": dateandtime,
             "diagonistics": diagonistics,
             "file_path": save_path
         }

        prescribe_collection.insert_one(prescribe_data)

         # Return response
        return jsonify({"message": "Prescription created successfully", "file_path": save_path}),200

    except Exception as e:
       messagetype ='error'
       message = f"Error generating prescription: {str(e)}"
       filelocation ='patientops/createprescription.py'
       generatelogs(messagetype,message,filelocation)
       return jsonify({"error":"Failed to create prescription"}),500

