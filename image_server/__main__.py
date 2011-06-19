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


@bottle.route('/')
@bottle.route('/p/:page#[0-9]*#')
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
    bottle.response.content_type = 'text/html'
    templ = os.path.join(os.path.dirname(__file__), 'image_serve_bottle.template')
    return bottle.template(templ, images=local_images,
                    prev_page_num=page - 1, next_page_num=page + 1, movedirs=ARGS.movedirs,
                    thumbsize=ARGS.thumbsize)


@bottle.route('/image/:image_type#(i|t)#/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg)#')
def read_images(image_type, image_name_ext):
    cType = {"png": "images/png", "jpg": "image/jpeg", "jpeg": "image/jpeg",
             "gif": "image/gif", "ico": "image/x-icon"}
    image_name, image_ext = re.search('(.*)\.(png|jpg|gif|ico)', image_name_ext).groups()
    bottle.response.content_type = cType[image_ext]
    if image_name_ext in os.listdir(ARGS.imagedir):  # Security
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        if image_type == 't':
            img = Image.open(image_path)
            width, height = img.size
            width = int(width * ARGS.thumbsize / float(height))
            img = img.resize((width, ARGS.thumbsize))
            print img.size
            fp = StringIO.StringIO()
            img.save(fp, image_ext if image_ext != 'jpg' else 'jpeg')
            fp.seek(0)
        else:
            fp = open(image_path)
        return fp.read()


@bottle.post('/move/:image_name_ext#(.*)\.(png|jpg|gif|ico|jpeg)#')
def move(image_name_ext):
    print(image_name_ext)
    if not ARGS.movedirs:
        bottle.abort(401)
    if image_name_ext in os.listdir(ARGS.imagedir):  # Security
        movedir = ARGS.movedirs[int(bottle.request.forms.get('index'))]
        image_path = os.path.join(ARGS.imagedir, image_name_ext)
        try:
            os.makedirs(movedir)
        except OSError:
            pass
        shutil.move(image_path, '%s/%s' % (movedir, image_name_ext))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Server a folder of images")
    # Webpy port
    parser.add_argument('--port', type=str, help='bottle.run webpy on this port',
                        default='8080')
    # Thumbnail size
    parser.add_argument('--thumbsize', type=int, help='maximum size in both directions (aspect ratio preserved) (default 50)',
                        default=50)

    # Image input directory
    parser.add_argument('--imagedir', type=str, help='folder of images, \
                        default \'.\'',
                        default='./')

    # Move images to this directory
    parser.add_argument('--movedirs', type=str,
                        help='click to move images to these (1+) directories',
                        action='append', default=[])

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
    bottle.run(host='0.0.0.0', port=ARGS.port, server='gevent', reloader=True)
