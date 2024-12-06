from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_proof():
    user_name = request.form['user_name']
    amount = request.form['amount']
    proof = request.files['proof']

    if proof:
        filename = f"{datetime.utcnow().timestamp()}_{proof.filename}"
        proof.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # บันทึกข้อมูลลงฐานข้อมูล
        new_transaction = Transaction(user_name=user_name, amount=amount, proof_image=filename)
        db.session.add(new_transaction)
        db.session.commit()
        flash('Proof uploaded successfully! Waiting for admin approval.')
        return redirect(url_for('index'))

@app.route('/admin')
def admin():
    transactions = Transaction.query.all()
    return render_template('admin.html', transactions=transactions)

@app.route('/approve/<int:id>')
def approve_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        transaction.status = "Approved"
        db.session.commit()
        flash(f"Transaction ID {id} has been approved.")
    return redirect(url_for('admin'))

@app.route('/reject/<int:id>')
def reject_transaction(id):
    transaction = Transaction.query.get(id)
    if transaction:
        transaction.status = "Rejected"
        db.session.commit()
        flash(f"Transaction ID {id} has been rejected.")
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)
