from flask import Flask, render_template, request, redirect, jsonify, session

app = Flask(__name__)
app.secret_key = 'uiehodknaiouhjeoi'

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate("kunci.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

@app.route('/api/mahasiswa')
def api_mahasiswa():
    daftar_mahasiswa = []
    # stream untuk mengambil semua
    docs = db.collection('mahasiswa').stream()
    for doc in docs:
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
    return jsonify(daftar_mahasiswa)

@app.route('/api/mahasiswa/<uid>')
def api_mahasiswa_detail(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return jsonify(mahasiswa)

@app.route('/login')
def login():
    if 'login' in session:
        return redirect('/')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/proseslogin', methods=["POST"])
def proseslogin():
    username_form = request.form.get("username")
    password_form = request.form.get("password")

    docs = db.collection('admin').where("username", "==", username_form).stream()
    for doc in docs:
        admin = doc.to_dict()
        print(admin)
        if admin['password'] == password_form:
            session['login'] = True
            return redirect('/')
    return render_template('login.html')

@app.route('/')
def index():
    if 'login' not in session:
        return redirect('/login')
    daftar_mahasiswa = []
    # stream untuk mengambil semua
    docs = db.collection('mahasiswa').stream()
    for doc in docs:
        mhs = doc.to_dict()
        mhs['id'] = doc.id
        daftar_mahasiswa.append(mhs)
    return render_template('index.html', daftar_mahasiswa=daftar_mahasiswa)

@app.route('/detail/<uid>')
def detail(uid):
    mahasiswa = db.collection('mahasiswa').document(uid).get().to_dict()
    return render_template('detail.html', mahasiswa=mahasiswa)

@app.route('/update/<uid>')
def update(uid):
    mhs = db.collection('mahasiswa').document(uid).get()
    mahasiswa = mhs.to_dict()
    mahasiswa['id'] = mhs.id
    return render_template('update.html', mhs=mahasiswa)

@app.route('/updatedata/<uid>', methods=["POST"])
def updatedata(uid):
    # ambil nilai formulir
    nama = request.form.get("nama")
    nilai = request.form.get("nilai")

    # update data ke firebase
    db.collection('mahasiswa').document(uid).update({
        'nama': nama,
        'nilai': int(nilai)
    })

    return redirect('/')

@app.route('/delete/<uid>')
def delete(uid):

    # delete data di firebase
    db.collection('mahasiswa').document(uid).delete()

    return redirect('/')

@app.route('/add', methods=["POST"])
def add_data():
    nama = request.form.get("nama")
    nilai = request.form.get("nilai")

    mahasiswa = {
        'alamat': 'Rumah',
        'email': 'mahasiswa@email.com',
        'nama': nama,
        'nilai': int(nilai),
        'foto': 'https://robohash.org/repudiandaenonqui.png?size=100x100&set=set1',
        'no_hp': '123456'
    }

    db.collection('mahasiswa').document().set(mahasiswa)
    
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
