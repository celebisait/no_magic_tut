import collections

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

CODE_TAG = '# CODE'
HTML_TAG = '# HTML'
TAGS = {HTML_TAG, CODE_TAG}

Part = collections.namedtuple('Part', ['tag', 'content'])
FORMATTER = HtmlFormatter(style='friendly')


def partition(template, source_lines):
  parts = []
  buffer_lines = []

  current_tag = None
  for line in source_lines:
    line = line.rstrip()
    if line not in TAGS:
      buffer_lines.append(line)
      continue
    if buffer_lines:
      parts.append(Part(current_tag, '\n'.join(buffer_lines)))
      buffer_lines = []
    current_tag = line

  if buffer_lines:
    parts.append(Part(current_tag, '\n'.join(buffer_lines)))
    buffer_lines = []

  return parts


IMAGE_PNG = "'image.png'"
ANIMATION_GIF = "'animation.mp4'"
ANIMATION_GIF = "'animation.mp4'"
image_counter = 0
animation_counter = 0


def add_image(image_name):
  return '<img src={}/>'.format(image_name)

def add_animation(animation_name):
  return """<video width="800" height="600" controls>
<source src={} type="video/mp4">
</video>""".format(animation_name)

def generate_code_html(source):
  global image_counter
  global animation_counter

  image_name = '"images/image{:03d}.png"'.format(image_counter)
  animation_name = '"animations/animation{:03d}.mp4"'.format(animation_counter)

  if IMAGE_PNG in source:
    highlighted = highlight(source, PythonLexer(), FORMATTER)
    source = source.replace(IMAGE_PNG, image_name)
    exec (source, globals())
    highlighted += add_image(image_name)
    image_counter += 1
  elif ANIMATION_GIF in source:
    highlighted = highlight(source, PythonLexer(), FORMATTER)
    source = source.replace(ANIMATION_GIF, animation_name)
    exec (source, globals())
    highlighted += add_animation(animation_name)
    animation_counter += 1

  return highlighted


def generate_html(template, source_lines):
  body = ''
  for part in partition(template, source_lines):
    if part.tag == HTML_TAG:
      body += part.content
    elif part.tag == CODE_TAG:
      body += generate_code_html(part.content.strip())

  return template.replace('$BODY', body)


def main():

  # write CSS file
  with open('pygments.css', 'w') as f:
    f.write(FORMATTER.get_style_defs('.highlight'))

  with open('template.data') as f:
    template = f.read()

  with open('source.nomagic') as f:
    source = f.readlines()

  output = generate_html(template, source)

  with open('output.html', 'w') as f:
    f.write(output)


main()
