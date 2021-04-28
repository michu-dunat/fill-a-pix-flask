from flask import Flask, render_template, request, flash, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
import game as game_module
import pickle
import jsonpickle

UPLOAD_FOLDER = 'uploaded_game_images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

app.secret_key = os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=('GET', 'POST'))
def index():
    if request.method == 'POST':
        username = request.form['username']
        rows = request.form['rows']
        columns = request.form['columns']
        file = request.files['image_file']
        error = None

        if not username:
            error = 'Username is required.'
        elif not rows:
            error = 'Number of rows is required.'
        elif not columns:
            error = 'Number of columns is required.'
        elif not file:
            error = 'File is required.'

        if file.filename == '':
            error = 'File is required.'

        if error is None and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['username'] = username
            file_path = f"{UPLOAD_FOLDER}/{filename}"
            game_object = game_module.Game(int(rows), int(columns), file_path)
            game_object_json = jsonpickle.encode(game_object)
            session['game_object'] = game_object_json
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


@app.route('/game', methods=('GET', 'POST'))
def game():
    is_game_finished = False
    game_object_json = session['game_object']
    game_object = jsonpickle.decode(game_object_json)
    is_guess_right = ''

    if request.method == 'POST':
        row_index = request.form['row_index']
        column_index = request.form['column_index']
        error = None
        if not row_index:
            error = 'Row index is required.'
        elif not column_index:
            error = 'Column index is required.'

        if error is None:
            is_guess_right = game_object.make_a_guess(int(row_index), int(column_index))
            is_game_finished = game_object.check_if_game_ended()
            game_object_json = jsonpickle.encode(game_object)
            session['game_object'] = game_object_json
        else:
            flash(error)

    return render_template("game.html", username=session['username'], game_board=game_object, is_game_finished=is_game_finished, is_guess_right=is_guess_right)


@app.route('/load/memory', methods=['POST'])
def load_from_memory():
    if request.method == 'POST':
        error = None
        if 'username' not in session or 'game_object' not in session:
            error = 'App memory is empty.'

        if error is None:
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


@app.route('/save/file', methods=['POST'])
def save_to_file():
    save_name = f"saves/{session['username']}"
    outfile = open(save_name, 'wb')
    game_object_json = session['game_object']
    game_object = jsonpickle.decode(game_object_json)
    pickle.dump(game_object, outfile)
    outfile.close()

    return redirect(url_for('game'))


@app.route('/load/file', methods=['POST'])
def load_from_file():
    if request.method == 'POST':
        username = request.form['username_save']
        error = None

        if not username:
            error = 'Username is required.'

        if error is None:
            save_name = f"saves/{username}"
            infile = open(save_name, 'rb')
            session['username'] = username
            game_object = pickle.load(infile)
            game_object_json = jsonpickle.encode(game_object)
            session['game_object'] = game_object_json
            infile.close()
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
