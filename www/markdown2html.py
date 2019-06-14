import markdown

# class Markdown2Html(object):
#     pass


def markdown2html(md):
    # exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite','markdown.extensions.tables','markdown.extensions.toc']
    html = markdown.markdown(md, extensions=['extra', 'codehilite', 'tables', 'toc'])
    return html
