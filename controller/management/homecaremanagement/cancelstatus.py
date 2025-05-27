@cancelstatusbp.route("/management/homecare/cancelstatus", methods=["POST"])
def cancelstatusfn():
    try:
        db = get_db_connection()
        homecarecol = db['homecare']
        uid = str(request.form.get('uid'))

        record = homecarecol.find_one({"uid": uid})
        if not record:
            return jsonify({"message": "No associated data found with the ID"}), 404

        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz)

        # Parse 'timefrom' from the DB
        scheduled_time_str = record.get('timefrom')
        if not scheduled_time_str:
            return jsonify({"error": "Scheduled time not found"}), 400

        try:
            # Attempt to parse datetime (update format accordingly if needed)
            scheduled_time = datetime.strptime(scheduled_time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=tz)
        except ValueError:
            return jsonify({"error": "Invalid datetime format in 'timefrom'. Expected 'YYYY-MM-DD HH:MM:SS'"}), 400

        time_difference = scheduled_time - current_time
        if time_difference.total_seconds() < 3600:
            return jsonify({"message": "Cannot cancel within 1 hour of the home care visit time"}), 403

        homecarecol.update_one({"uid": uid}, {"$set": {"status": "cancelled"}})
        return jsonify({"message": "Cancelled successfully"})

    except Exception as e:
        print(e)
        return jsonify({'error': f'{str(e)}'}), 500
