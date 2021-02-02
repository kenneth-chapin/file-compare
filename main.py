import os
from flask import Flask, render_template, request
from werkzeug.exceptions import BadRequestKeyError
from werkzeug.utils import redirect
from dumplicates import get_file_infos, show_finfos

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/')
@app.route('/index')
def hello():
    return render_template('index.html', data=[])


def get_form_val(val):
    try:
        return request.form.get(val)
    except BadRequestKeyError as err:
        print('failed to form data {}: {}'.format(val, err))
    return ''


@app.route('/start', methods=["GET", "POST"])
def home():
    if request.method == 'POST':
        dir = get_form_val('start')
        if os.path.isdir(dir):
            ext = get_form_val('ext')
            finfos = get_file_infos(dir, ext)
            dupes = bool(get_form_val('dupes'))
            if dupes:
                finfos = show_finfos(finfos)
            return render_template('index.html', data=finfos, dupes=dupes)
        else:
            print('{} is not a valid directory'.format(dir))
    return redirect('/index')


if __name__ == '__main__':
    app.run()
