from gevent import monkey
monkey.patch_all()
import bottle
bottle.debug(True)
from bottle import route, run, response, template, post, abort
import os
import argparse
import random
import re
import Image
import cStringIO as StringIO
import shutil

bottle.debug(True)
@route('/')
@route('/p/:page#[0-9]*#')
def main(page=''):
    if not page:
        page = '0'
    page = int(page)
    image_extensions = set(['jpg', 'png', 'jpeg', 'gif', 'ico'])
    extension = lambda x: x.split('.')[-1] if '.' in x else ''
    local_images = [x for x in sorted(os.listdir(ARGS.imagedir), reverse=ARGS.reverse)
                    if extension(x) in image_extensions]
    if ARGS.random:
        local_images = random.sample(local_images, min(ARGS.limit,
                                                       len(local_images)))
    else:
        local_images = local_images[ARGS.limit * page:ARGS.limit * (page + 1)]
    response.content_type = 'text/html'
    templ = os.path.join(os.path.dirname(__file__), 'image_serve_template')
    return template(templ, images=local_images,
                    prev_page_num=page - 1, next_page_num=page + 1, movedir=ARGS.movedir)


@route('/image/:image_type#(i|t)#/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg)#')
def read_images(image_type, image_name_ext):
    cType = {"png": "images/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
             "gif": "image/gif", "ico": "image/x-icon"}
    image_name, image_ext = re.search('(.*)\.(png|jpg|gif|ico)', image_name_ext).groups()
    response.content_type = cType[image_ext]
    if image_name_ext in os.listdir(ARGS.imagedir):  # Security
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        if image_type == 't':
            img = Image.open(image_path)
            width, height = img.size
            width = int(width * 50 / float(height))
            img = img.resize((width, 50))
            fp = StringIO.StringIO()
            img.save(fp, image_ext if image_ext != 'jpg' else 'jpeg')
            fp.seek(0)
        else:
            fp = open(image_path)
        return fp.read()


@post('/move/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg)#')
def move(image_name_ext):
    print(image_name_ext)
    if ARGS.movedir is None:
        abort(401)
    if image_name_ext in os.listdir(ARGS.imagedir):  # Security
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        try:
            os.makedirs(ARGS.movedir)
        except OSError:
            pass
        shutil.move(image_path, '%s/%s' % (ARGS.movedir, image_name_ext))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server a folder of images")
    # Webpy port
    parser.add_argument('--port', type=str, help='run webpy on this port',
                        default='8080')
    # Image input directory
    parser.add_argument('--imagedir', type=str, help='folder of images, \
                        default \'.\'',
                        default='./')
    # Move images to this directory
    parser.add_argument('--movedir', type=str,
                        help='click to move images to this directory',
                        default=None)
    # Limit number of images to display
    parser.add_argument('--limit', type=int,
                        help='show at most LIMIT images (default 200)',
                        default=200)
    # Sort order
    parser.add_argument('--reverse', type=bool,
                        help='Reverse the sort',
                        default=False)
    # Randomize each time
    parser.add_argument('--random', action='store_true',
                        help='randomly sample images in the folder each time')
    # These args are used as global variables
    ARGS = parser.parse_args()
    run(host='0.0.0.0', port=ARGS.port, server='gevent', reloader=True)
