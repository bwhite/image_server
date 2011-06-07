import web
import os
import web
import cStringIO as StringIO
import Image

urls = ('/', 'main',
        '/p/(\d+)', 'main',
        '/i/(.*)\.(png|jpg|gif|ico)', 'images', #this is where the image folder is located....
        '/t/(.*)\.(png|jpg|gif|ico)', 'thumb_images' #this is where the image folder is located....
        )

class main(object):
    def GET(self, page=0):
        num_per_page = 50
        page = int(page)
        image_extensions = set(['jpg', 'png', 'jpeg', 'gif', 'ico'])
        extension = lambda x: x.split('.')[-1] if '.' in x else ''
        local_images = [x for x in sorted(os.listdir('.')) if extension(x) in image_extensions]
        local_images = local_images[num_per_page * page:num_per_page * (page + 1)]
        web.header("Content-Type", 'text/html')
        render = web.template.frender(os.path.dirname(__file__) + '/image_serve_template.html')
        return render(local_images, str(page - 1), str(page + 1))

class images(object):
    def GET(self, name, extension):
        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"            }
        file_name = '%s.%s' % (name, extension)
        if file_name in os.listdir('.'):  # Security
            web.header("Content-Type", cType[extension]) # Set the Header
            return open(file_name).read()
        else:
            raise web.notfound()

class thumb_images(object):
    def GET(self, name, extension):
        cType = {
            "png":"images/png",
            "jpg":"image/jpeg",
            "gif":"image/gif",
            "ico":"image/x-icon"            }
        file_name = '%s.%s' % (name, extension)
        if file_name in os.listdir('.'):  # Security
            web.header("Content-Type", cType[extension]) # Set the Header
            img = Image.open(file_name)
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
    app.run()
