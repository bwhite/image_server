import web
import os
import cStringIO as StringIO
import Image
import argparse
import shutil
import sys

urls = ('/', 'main',

        # POST to move the images
        '/move/(.*)', 'move',

        # this is where the image folder is located....
        '/i/(.*)\.(png|jpg|gif|ico)', 'images',

        # this is where the image folder is located....
        '/t/(.*)\.(png|jpg|gif|ico)', 'thumb_images'
        )


class main(object):
    def GET(self):
        image_extensions = set(['jpg', 'png', 'jpeg', 'gif', 'ico'])
        extension = lambda x: x.split('.')[-1] if '.' in x else ''
        local_images = [x for x in sorted(os.listdir(ARGS.imagedir))
                        if extension(x) in image_extensions]
        web.header("Content-Type", 'text/html')
        render = web.template.frender(os.path.dirname(__file__) +
                                      '/image_serve_template.html')
        return render(ARGS, local_images)


class move(object):
    def POST(self, file_name):
        print 'MOVE ', file_name
        # Only accept move posts if the command line argument is set
        if ARGS.movedir is None:
            return web.notfound()

        if file_name in os.listdir(ARGS.imagedir):
            # Move the image
            try:
                shutil.move(os.path.join(ARGS.imagedir, file_name),
                            '%s/%s' % (ARGS.movedir, file_name))
            except Exception, e:
                print e
                raise web.internalerror(e)
        else:
            raise web.notfound()


class images(object):
    def GET(self, name, extension):
        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"
            }
        file_name = '%s.%s' % (name, extension)
        if file_name in os.listdir(ARGS.imagedir):  # Security
            web.header("Content-Type", cType[extension])  # Set the Header
            return open(os.path.join(ARGS.imagedir, file_name)).read()
        else:
            raise web.notfound()


class thumb_images(object):
    def GET(self, name, extension):
        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"
            }
        file_name = '%s.%s' % (name, extension)
        if file_name in os.listdir(ARGS.imagedir):  # Security
            web.header("Content-Type", cType[extension])  # Set the Header
            img = Image.open(os.path.join(ARGS.imagedir, file_name))
            width, height = img.size
            width = int(width * 50 / float(height))
            img = img.resize((width, 50))
            fp = StringIO.StringIO()
            img.save(fp, extension if extension != 'jpg' else 'jpeg')
            fp.seek(0)
            return fp.read()
        else:
            raise web.notfound()


app = web.application(urls, globals())

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
                        help='show at most LIMIT images (0 for all images, \
                        default 200)',
                        default=200)

    # These args are used as global variables
    ARGS = parser.parse_args()

    sys.argv = ['', ARGS.port]
    app.run()
