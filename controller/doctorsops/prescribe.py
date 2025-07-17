import uuid
import random
import string
from flask import Blueprint, jsonify, request
import os
from pymongo import MongoClient
import pytz
from utils.logs import generatelogs
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
import textwrap
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = 'uploads/medicaldirectory/prescribe/'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    client = MongoClient(os.getenv('MONGODB_URI'))
    db = client[os.getenv('DB_NAME')]
    return db

def wrap_text(pdf_canvas, text, max_width):
    """Wraps text to fit within a specified width."""
    wrapped_lines = []
    initial_wrap = textwrap.wrap(text, width=95)

    for line in initial_wrap:
        while pdf_canvas.stringWidth(line, 'Helvetica', 12) > max_width:
            split_index = max_width // 6
            while split_index > 0 and line[split_index] != ' ':
                split_index -= 1
            if split_index == 0:
                split_index = len(line)
            wrapped_lines.append(line[:split_index])
            line = line[split_index:].lstrip()
        if line:
            wrapped_lines.append(line)
    return wrapped_lines

def generate_prescription_id(length=6):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

prescribe_bp = Blueprint('prescribe_bp', __name__)

@prescribe_bp.route('/createprescription', methods=['POST'])
def createprescribfn():
    try:
        prescription_id = generate_prescription_id()

        hospitalname = str(request.form.get('hospitalname'))
        doctorid = str(request.form.get('doctorid'))
        patientid = str(request.form.get('patientid'))
        dateandtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        diagonistics = str(request.form.get('diagonistics'))
        medicine = str(request.form.get('medicine'))

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

        unique_filename = f"prescription_{uuid.uuid4().hex}.pdf"
        save_path = os.path.join(UPLOAD_FOLDER, unique_filename)

        pdf = canvas.Canvas(save_path, pagesize=A4)
        width, height = A4

        # Header
        pdf.setFillColor(HexColor("#4A90E2"))
        pdf.rect(0, height - 120, width, 120, fill=1)
        pdf.drawImage('./static/logo.jpg', 20, height - 100, width=80, height=80)
        pdf.setFont("Helvetica-Bold", 24)
        pdf.setFillColor(HexColor("#FFFFFF"))
        pdf.drawCentredString(width / 2, height - 70, hospitalname)
        pdf.setFont("Helvetica", 12)
        pdf.drawCentredString(width / 2, height - 90, f"Prescription ID: {prescription_id.lower()}")

        # Doctor Info
        pdf.setFont("Helvetica", 14)
        pdf.setFillColor(HexColor("#333333"))
        pdf.drawString(20, height - 150, f"Doctor: {doctorfullname}")
        pdf.drawString(20, height - 170, f"Qualification: {docqualification}")
        pdf.drawString(20, height - 190, f"Specialization: {docspecialization}")

        # Patient Info
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(20, height - 220, "Patient Details:")
        pdf.setFont("Helvetica", 14)
        pdf.drawString(20, height - 240, f"Name: {patientfirstname} {patientlastname}")

        # Diagnostics
        pdf.setFont("Helvetica-Bold", 16)
        diagnostics_title = "Diagnostics:"
        title_width = pdf.stringWidth(diagnostics_title, "Helvetica-Bold", 16)
        pdf.drawString((width - title_width) / 2, height - 260, diagnostics_title)

        pdf.setFont("Helvetica", 12)
        diagnostics_lines = wrap_text(pdf, diagonistics, max_width=width - 40)
        for i, line in enumerate(diagnostics_lines):
            line_width = pdf.stringWidth(line, "Helvetica", 12)
            pdf.drawString((width - line_width) / 2, height - (280 + i * 15), line)

        # Medicines
        line_y_start = height - (280 + len(diagnostics_lines) * 15)
        pdf.setFont("Helvetica-Bold", 16)
        medicine_title = "Medicines:"
        title_width = pdf.stringWidth(medicine_title, "Helvetica-Bold", 16)
        pdf.drawString((width - title_width) / 2, line_y_start - 20, medicine_title)

        pdf.setFont("Helvetica", 12)
        medicine_lines = wrap_text(pdf, medicine, max_width=width - 40)
        for j, med_line in enumerate(medicine_lines):
            med_line_width = pdf.stringWidth(med_line, "Helvetica", 12)
            pdf.drawString((width - med_line_width) / 2, line_y_start - 40 - (j * 15), med_line)

        # Adjust footer position based on content
        footer_y_offset = line_y_start - 60 - (len(medicine_lines) * 15)
        if footer_y_offset < 100:
            footer_y_offset = 100

        # Date (top right)
        pdf.setFont("Helvetica", 12)
        pdf.drawString(width - 180, height - 40, f"Date: {dateandtime}")

        # Footer
        footer_height = 0.75 * inch
        pdf.setFillColor(HexColor("#E94E77"))
        pdf.rect(0, 0, width, footer_height, fill=1)
        pdf.setFillColor(HexColor("#FFFFFF"))
        pdf.setFont("Helvetica", 10)
        pdf.drawString(20, 0.25 * inch, f"© {hospitalname}")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pdf.drawString(width - 180, 0.25 * inch, f"Generated on: {timestamp}")

        # Save PDF
        pdf.save()

        prescribe_data = {
            "hospitalname": hospitalname,
            "patientfullname": patientfirstname + ' ' + patientlastname,
            "dateandtime": dateandtime,
            "diagonistics": diagonistics,
            "medicine": medicine,
            "file_path": save_path,
            "patientid": patientid,
            "doctorid": doctorid,
            "prescription_id": prescription_id,
            "guestaccess": "no",
            "created_at": datetime.now(pytz.timezone('Asia/Kolkata')).isoformat()
        }

        prescribe_collection.insert_one(prescribe_data)

        return jsonify({
            "message": "Prescription created successfully",
            "file_path": save_path
        }), 200

    except Exception as e:
        messagetype = 'error'
        message = f"Error generating prescription: {str(e)}"
        filelocation = 'patientops/createprescription.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": "Failed to create prescription"}), 500
