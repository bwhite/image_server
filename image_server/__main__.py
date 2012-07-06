import gevent
from gevent import monkey
monkey.patch_all()
import bottle
import os
import argparse
import random
import re
import Image
import cStringIO as StringIO
import shutil
import math
import urllib
from static_server.auth import verify
bottle.debug(True)


def find_local_images():
    image_extensions = set(['jpg', 'png', 'jpeg', 'gif', 'ico', 'pgm', 'ppm'])
    extension = lambda x: x.split('.')[-1] if '.' in x else ''
    images = [x for x in sorted(os.listdir(ARGS.imagedir), reverse=ARGS.reverse)
              if extension(x) in image_extensions]
    if ARGS.random:
        random.shuffle(images)
    return images


def find_page_images():
    images = find_local_images()
    limit = ARGS.limit
    num_pages = int(math.ceil(len(images) / float(limit)))
    page_images = [images[p * limit:(p + 1) * limit] for p in range(num_pages)]
    local_images = {}
    # We need a mapping from images to page numbers to properly clean up when we move
    for num, p in enumerate(page_images):
        for i in p:
            local_images[i] = num
    return page_images, local_images


def make_thumbnail(image_path):
    try:
        img = Image.open(image_path)
    except IOError:
        if ARGS.baddir:
            gevent.Greenlet(move_task, os.path.basename(image_path), ARGS.baddir).start()
            raise IOError('Cannot read [%s].  Moving to [%s]' % (image_path, ARGS.baddir))
        else:
            raise IOError('Cannot read [%s]' % image_path)
    try:
        image_ext = re.search('.*\.(png|jpg|gif|ico|jpeg|ppm|pgm)', image_path).group(1)
    except AttributeError:
        raise ValueError('Unknown extension on [%s]' % image_path)
    width, height = img.size
    width = int(width * ARGS.thumbsize / float(height))
    img = img.resize((width, ARGS.thumbsize))
    fp = StringIO.StringIO()
    if img.mode in ('P', 'RGBA'):
        img = img.convert('RGB')
    img.save(fp, image_ext if image_ext != 'jpg' else 'jpeg')
    fp.seek(0)
    return fp.read()


@bottle.route('/')
@bottle.route('/p/:page#[0-9]*#')
@verify(lambda : ARGS.noauth)
def main(page=''):
    if not page:
        page = '0'
    page = int(page)
    local_images = PAGE_IMAGES[page]
    bottle.response.content_type = 'text/html'
    templ = os.path.join(os.path.dirname(__file__), 'image_serve_template')
    prev_page_num = page - 1 if page - 1 >= 0 else None
    next_page_num = page + 1 if page + 1 < len(PAGE_IMAGES) else None
    return bottle.template(templ, images=local_images,
                           prev_page_num=prev_page_num,
                           next_page_num=next_page_num,
                           movedirs=ARGS.movedirs,
                           thumbsize=ARGS.thumbsize)


@bottle.route('/image/:image_type#(i|t)#/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg|ppm|pgm)#')
@verify(lambda : ARGS.noauth)
def read_images(image_type, image_name_ext):
    cType = {"png": "images/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
             "gif": "image/gif", "ico": "image/x-icon", "pgm": "image/x-pgm",
             "ppm": "image/x-ppm"}
    image_ext = re.search('.*\.(png|jpg|gif|ico|jpeg|ppm|pgm)', image_name_ext).group(1)
    bottle.response.content_type = cType[image_ext]
    image_name_ext = urllib.unquote(image_name_ext).decode('utf8')
    if image_name_ext in LOCAL_IMAGES:  # Security
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        if image_type == 't':
            if image_name_ext in THUMB_CACHE and os.path.exists(image_path):
                out = THUMB_CACHE[image_name_ext]
            else:
                if len(THUMB_CACHE) >= ARGS.thumbcachesize:
                    try:
                        del THUMB_CACHE[random.choice(THUMB_CACHE)]
                    except KeyError:
                        pass
                out = THUMB_CACHE[image_name_ext] = make_thumbnail(image_path)
        else:
            fp = open(image_path)
            out = fp.read()
        return out


@bottle.route('/refresh/')
@verify(lambda : ARGS.noauth)
def refresh():
    global PAGE_IMAGES, LOCAL_IMAGES
    PAGE_IMAGES, LOCAL_IMAGES = find_page_images()
    bottle.redirect('/')


def move_task(image_name_ext, movedir):
    if image_name_ext in LOCAL_IMAGES:  # Security
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        try:
            os.makedirs(movedir)
        except OSError:
            pass
        try:
            shutil.move(image_path, '%s/%s' % (movedir, image_name_ext))
        except IOError:
            pass
        PAGE_IMAGES[LOCAL_IMAGES[image_name_ext]].remove(image_name_ext)
        del LOCAL_IMAGES[image_name_ext]


@bottle.post('/move/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg|ppm|pgm)#')
def move(image_name_ext):
    if not ARGS.movedirs:
        bottle.abort(401)
    gevent.Greenlet(move_task, image_name_ext, ARGS.movedirs[int(bottle.request.forms.get('index'))]).start()


def fill_cache():
    for image_name_ext in find_local_images():
        gevent.sleep()
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        try:
            THUMB_CACHE[image_name_ext] = make_thumbnail(image_path)
        except IOError, e:
            print(e)
            continue
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve a folder of images")
    # Webpy port
    parser.add_argument('--port', type=str, help='Run on this port (default 8080)',
                        default='8080')
    # Thumbnail size
    parser.add_argument('--thumbsize', type=int, help='maximum size in both directions (aspect ratio preserved) (default 100)',
                        default=100)

    # Image input directory
    parser.add_argument('--imagedir', type=str, help='folder of images, \
                        default \'.\'',
                        default='./')

    # Move images to this directory
    parser.add_argument('--movedirs', type=str,
                        help='click to move images to these (1+) directories',
                        action='append', default=[])

    # Move images to this directory
    parser.add_argument('--baddir', type=str,
                        help='All unreadable images are moved here (off by default)',
                        default='')

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
    # Number of thumbnails to cache
    parser.add_argument('--thumbcachesize', default=1000,
                        help='Number of thumbnails to cache (default 1000)')
    parser.add_argument('--noauth', action='store_false')
    # These args are used as global variables
    ARGS = parser.parse_args()
    THUMB_CACHE = {}
    PAGE_IMAGES, LOCAL_IMAGES = find_page_images()
    gevent.Greenlet(fill_cache).start_later(1)  # Give the server a second to start
    bottle.run(host='0.0.0.0', port=ARGS.port, server='gevent')
