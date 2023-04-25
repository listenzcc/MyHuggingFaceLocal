"""
File: app.py
Author: Chuncheng Zhang
Date: 2023-04-17
Functions:
    1. Imports
    2. Flask app routes
    3. Main jobs
    4. Pending
    5. Pending
"""


# %% ---- 2023-04-17 ------------------------
# Imports
import time
import json
import flask
import argparse
import traceback
import threading

from pathlib import Path
from copy import deepcopy

# %%
parser = argparse.ArgumentParser(
    prog='Stable diffusion project',
    description='Stable diffusion project in Flask application.'
)

parser.add_argument(
    '--no-models',
    action='store_true',
    help='Toggle debug mode, it disables the large models from loading'
)

args = parser.parse_args()


# %%
no_models = args.no_models


if not no_models:
    from module.txt2img import perform_txt2img, opt_txt2img
    from module.img2img import perform_img2img, opt_img2img
else:
    class Option(object):
        def __init__(self):
            self.prompt = ''
            self.outdir = ''

    opt_txt2img = Option()
    opt_img2img = Option()

    def perform_txt2img(opt):
        assert False, 'Invalid perform_txt2img function, since the flask app is started with no-models mode'
        return

    def perform_img2img(opt):
        assert False, 'Invalid perform_img2img function, since the flask app is started with no-models mode'
        return

    print('!!!!!!!!!!!!! The flask app is started with debug mode, its startup is quick but without large model response')


# %% ---- 2023-04-17 ------------------------
# Flask app and its routings
root = Path(__file__).parent
html_root = root.joinpath('html')
data_root = root.joinpath('outputs')

app = flask.Flask(__name__, static_folder=html_root.joinpath('static'))


def error_response():
    '''
    Handle on unsuccessful response,
    it refers unexpected error happens.
    '''
    content = dict(
        status='Unknown error',
        detail=traceback.format_exc()
    )
    return flask.make_response(content, 500)


# %% ---- 2023-04-17 ------------------------
# Routing for files
@app.route('/')
def _index():
    return open(html_root.joinpath('index.html')).read()


@app.route('/src/<filename>')
def _src(filename):
    resp = flask.make_response(
        open(html_root.joinpath(f'src/{filename}')).read())
    resp.headers['Content-Type'] = 'application/javascript'
    return resp
    return open(html_root.joinpath(f'src/{filename}')).read()


# @app.route('/static/<filename>')
# def _static(filename):
#     return open(html_root.joinpath(f'static/{filename}')).read()


# %%
# Routing for img2img operations
@app.route('/operation/img2img')
def _operation_img2img():
    '''
    Perform img2img operation by given prompt,
    It costs about -- seconds.

    It returns the path list of the generated images.
    '''

    try:
        args = flask.request.args
        prompt = args.get('prompt', '')

        initImg = args.get('initImg', '')
        init_img = data_root.joinpath(initImg)
        assert Path(init_img).is_file(
        ), 'The initImg is not a file, check the param of initImg {}.'.format(initImg)

        opt = deepcopy(opt_img2img)
        opt.prompt = prompt
        opt.init_img = init_img.as_posix()

        print('------------------------------------------------------------')
        print('Working with prompt: {} on img: {}'.format(prompt, init_img))
        print('Working with opt: {}'.format(opt.__dict__))

        tic = time.time()
        img_path_list = perform_img2img(opt)
        img_path_list = [Path(e).relative_to(data_root).as_posix()
                         for e in img_path_list]
        toc = time.time()

        print('The img2img costs {} seconds, generates images: {}'.format(
            toc-tic, img_path_list))

        return json.dumps(img_path_list)

    except:
        return error_response()
    pass


# Routing for txt2img operations
@app.route('/operation/txt2img')
def _operation_txt2img():
    '''
    Perform txt2img operation by given prompt,
    It costs about 30 seconds.

    It returns the path list of the generated images.
    '''

    try:
        args = flask.request.args
        prompt = args.get('prompt', '')

        opt = deepcopy(opt_txt2img)
        opt.prompt = prompt

        print('-------------------------')
        print(f'The txt2img receives {prompt}.')
        print('Working with opt: {}'.format(opt.__dict__))

        tic = time.time()
        img_path_list = perform_txt2img(opt)
        img_path_list = [Path(e).relative_to(data_root).as_posix()
                         for e in img_path_list]
        toc = time.time()

        print('The txt2img costs {} seconds, generates images: {}'.format(
            toc-tic, img_path_list))

        return json.dumps(img_path_list)

    except:
        return error_response()


# Routing for img folders
@app.route('/request/txt2img/history')
def _request_txt2img_history():
    '''
    Request the folder of the images.

    The response is a JSON object with
    - folder: The folder name;
    - images: The list of the image path.
    '''

    args = flask.request.args
    limit = args.get('limit', 100)

    folder_list = sorted([dict(folder=e)
                          for e in
                          Path(data_root, 'txt2img').iterdir()
                          if e.is_dir()],
                         key=lambda d: d['folder'],
                         reverse=True)[:limit]

    try:
        for e in folder_list:
            p = e['folder']
            e['images'] = sorted([e.relative_to(data_root).as_posix()
                                  for e in p.joinpath('samples').iterdir()])
            e['setup'] = json.load(open(p.joinpath('setup.json'), 'r'))

            # Reading is finished, change the pathlib object into posix
            e['folder'] = p.relative_to(data_root).as_posix()

        response = flask.make_response(json.dumps(folder_list))
        response.headers['Content-Type'] = 'application/json'
        return response
    except:
        return error_response()


# Routing for request images
@app.route('/request/img')
def _request_img():
    '''
    Request image at given path.

    The path is relative to the data_root directory.
    '''

    args = flask.request.args
    path = args.get('path', None)

    if path is None:
        return flask.make_response('Failed request/img, since [?path] is required', 404)

    path = data_root.joinpath(path)
    if not path.is_file():
        return flask.make_response('Failed request/img, since Path [{}] does not exist'.format(path), 404)

    try:
        image_data = open(path, 'rb').read()
        response = flask.make_response(image_data)
        response.headers['Content-Type'] = 'image/png'
        return response

    except:
        return error_response()


# %% ---- 2023-04-17 ------------------------
# Main jobs
if __name__ == '__main__':
    app.run('0.0.0.0', port=8123)
    # app.run(port=8890)


# %% ---- 2023-04-17 ------------------------
# Pending


# %% ---- 2023-04-17 ------------------------
# Pending
