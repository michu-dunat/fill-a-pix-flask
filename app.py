from flask import Flask, render_template, request, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
import Game as fill_a_pix
import pickle

UPLOAD_FOLDER = 'files'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app = Flask(__name__)

app.secret_key = os.urandom(16)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


GAME_OBJECT = None
USERNAME = None


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=('GET', 'POST'))
def index():
    global GAME_OBJECT
    global USERNAME

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
            USERNAME = username
            file_path = f"{UPLOAD_FOLDER}/{filename}"
            GAME_OBJECT = fill_a_pix.Game(int(rows), int(columns), file_path)
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


@app.route('/game', methods=('GET', 'POST'))
def game():
    global USERNAME
    global GAME_OBJECT

    is_game_finished = False

    if request.method == 'POST':
        row_index = request.form['row_index']
        column_index = request.form['column_index']
        error = None
        if not row_index:
            error = 'Row index is required.'
        elif not column_index:
            error = 'Column index is required.'

        if error is None:
            GAME_OBJECT.make_a_guess(int(row_index), int(column_index))
            is_game_finished = GAME_OBJECT.check_if_game_ended()
        else:
            flash(error)

    return render_template("game.html", username=USERNAME, game_board=GAME_OBJECT, is_game_finished=is_game_finished)


@app.route('/load/memory', methods=['POST'])
def load_from_memory():
    global USERNAME
    global GAME_OBJECT

    if request.method == 'POST':
        error = None
        if not USERNAME or not GAME_OBJECT:
            error = 'App memory is empty.'

        if error is None:
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


@app.route('/save/file', methods=['POST'])
def save_to_file():
    global USERNAME
    global GAME_OBJECT

    save_name = f"saves/{USERNAME}"
    outfile = open(save_name, 'wb')
    pickle.dump(GAME_OBJECT, outfile)
    outfile.close()

    return redirect(url_for('game'))


@app.route('/load/file', methods=['POST'])
def load_from_file():
    global USERNAME
    global GAME_OBJECT

    if request.method == 'POST':
        username = request.form['username_save']
        error = None

        if not username:
            error = 'Username is required.'

        if error is None:
            save_name = f"saves/{username}"
            infile = open(save_name, 'rb')
            USERNAME = username
            GAME_OBJECT = pickle.load(infile)
            infile.close()
            return redirect(url_for('game'))

        flash(error)

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
