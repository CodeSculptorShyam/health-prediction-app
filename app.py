import os
from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify
)

from database import (
    init_db, create_patient, get_all_patients,
    get_patient, update_patient, delete_patient
)
from validators import validate_patient
from ai_service import generate_health_remark
from validators import validate_email

app = Flask(__name__)
app.secret_key = os.environ.get(
    "FLASK_SECRET_KEY", "local-development-only-change-me"
)

init_db()




def prepare_patient(form_data):
    cleaned, errors = validate_patient(form_data)

    if errors:
        return None, errors

    cleaned["remarks"] = generate_health_remark(
        cleaned["glucose"],
        cleaned["haemoglobin"],
        cleaned["cholesterol"],
    )
    return cleaned, {}



def ai_unavailable(remark):
    return (
        remark.startswith("AI assessment unavailable")
        or remark.startswith("AI assessment could not")
    )


@app.route("/")
def index():
    return render_template("index.html", patients=get_all_patients())


@app.route("/patients", methods=["POST"])
def add_patient():
    cleaned, errors = prepare_patient(request.form)
    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("index"))

    patient_id = create_patient(cleaned)
    if ai_unavailable(cleaned["remarks"]):
        flash(
            f"Patient saved (ID {patient_id}), but AI remarks are unavailable. "
            "Check API configuration.",
            "warning",
        )
    else:
        flash("Patient record created successfully.", "success")
    return redirect(url_for("index"))


@app.route("/patients/<int:patient_id>/edit", methods=["GET", "POST"])
def edit_patient(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        flash("Patient record not found.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        cleaned, errors = prepare_patient(request.form)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template("edit.html", patient=patient)

        update_patient(patient_id, cleaned)
        if ai_unavailable(cleaned["remarks"]):
            flash(
                "Record updated, but AI remarks are unavailable. "
                "Check API configuration.",
                "warning",
            )
        else:
            flash("Patient record updated successfully.", "success")
        return redirect(url_for("index"))

    return render_template("edit.html", patient=patient)


@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
def remove_patient(patient_id):
    if delete_patient(patient_id):
        flash("Patient record deleted.", "success")
    else:
        flash("Patient record not found.", "danger")
    return redirect(url_for("index"))


@app.route("/api/patients", methods=["GET"])
def api_get_patients():
    return jsonify(get_all_patients()), 200


@app.route("/api/patients", methods=["POST"])
def api_create_patient():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"errors": ["A JSON object is required."]}), 400

    cleaned, errors = prepare_patient(data)
    if errors:
        return jsonify({"errors": errors}), 400

    patient_id = create_patient(cleaned)
    return jsonify(get_patient(patient_id)), 201


@app.route("/api/patients/<int:patient_id>", methods=["GET"])
def api_get_patient(patient_id):
    patient = get_patient(patient_id)
    if not patient:
        return jsonify({"error": "Patient not found."}), 404
    return jsonify(patient), 200


@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
def api_update_patient(patient_id):
    if not get_patient(patient_id):
        return jsonify({"error": "Patient not found."}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"errors": ["A JSON object is required."]}), 400

    cleaned, errors = prepare_patient(data)
    if errors:
        return jsonify({"errors": errors}), 400

    update_patient(patient_id, cleaned)
    return jsonify(get_patient(patient_id)), 200


@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def api_delete_patient(patient_id):
    if delete_patient(patient_id):
        return jsonify({"message": "Patient deleted successfully."}), 200
    return jsonify({"error": "Patient not found."}), 404


if __name__ == "__main__":
    # Debug mode is for local development only.
    app.run(debug=True)
