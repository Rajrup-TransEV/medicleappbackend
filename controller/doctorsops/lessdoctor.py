@lessdocbp.route('/selectivedoctordata', methods=['POST'])
def lessdocbpfn():
    doctorspecialization = str(request.form.get('doctorspecialization')).lower()
    try:
        db = get_db_connection()
        doctor_collection = db['doctors']
        timetable_collection = db['doctortimetable']

        # Fetch doctors by specialization
        doctors = list(doctor_collection.find({"specialization": doctorspecialization}))
        
        if not doctors:
            return jsonify({"error": "No doctors found!"}), 404

        doctor_data_list = []

        for doctor in doctors:
            doctor_id = doctor.get('uid')

            # Fetch all timetable entries for this doctor
            timetables = list(timetable_collection.find({"doctorid": doctor_id}))
            formatted_timetables = []
            for t in timetables:
                formatted_timetables.append({
                    "date": t.get("date"),
                    "schedule": t.get("schedule")
                })

            doctor_payload = {
                "uid": doctor.get('uid'),
                "fullname": doctor.get('fullname'),
                "timetable": formatted_timetables
            }

            doctor_data_list.append(doctor_payload)

        generatelogs('success', 'Doctor data has been fetched successfully', 'lessdoctor.py')
        return jsonify({"message": "Doctor data has been fetched successfully", "data": doctor_data_list}), 200

    except Exception as e:
        messagetype = 'error'
        message = f"Error while fetching doctor data: {str(e)}"
        filelocation = 'lessdoctor.py'
        generatelogs(messagetype, message, filelocation)
        return jsonify({"error": str(e)}), 500
