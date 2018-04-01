import sys
import collections
import StringIO
import contextlib
import datetime
import time

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


@contextlib.contextmanager
def stdoutIO(stdout=None):
  old = sys.stdout
  if stdout is None:
    stdout = StringIO.StringIO()
  sys.stdout = stdout
  yield stdout
  sys.stdout = old


CODE_TAG = '# CODE'
HTML_TAG = '# HTML'
HEADER_TAG = '# HEADER'
PSEUDO_TAG = '# PSEUDO'
LAST_UPDATED_TAG = '# LAST_UPDATED'

TAGS = {HTML_TAG, CODE_TAG, HEADER_TAG, PSEUDO_TAG, LAST_UPDATED_TAG}

Part = collections.namedtuple('Part', ['tag', 'content', 'info'])
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
      parts.append(
          Part(current_tag, '\n'.join(buffer_lines[1:]), eval(buffer_lines[0])))
      buffer_lines = []
    current_tag = line

  if buffer_lines:
    parts.append(
        Part(current_tag, '\n'.join(buffer_lines[1:]), eval(buffer_lines[0])))
    buffer_lines = []

  return parts


IMAGE_PNG = "'image.png'"
ANIMATION_GIF = "'animation.mp4'"
PRINT = "print"
image_counter = 0
animation_counter = 0


def add_image(image_name, width):
  return '<img class="generated_image" width="{}" src={}/>'.format(width, image_name)


def add_header(header_title):
  header_id = header_title.lower().replace(' ', '_')
  return '<a href="#{}" class="header_style">  <h1 id="{}">{}</h1>  </a>'.format(
                              header_id, header_id, header_title)


def add_animation(animation_name, width):
  return """<video class="generated_video" width="{}" controls>
<source src={} type="video/mp4">
</video>""".format(width, animation_name)

def add_last_updated():
  dt = datetime.datetime.now()
  return '<center>Last updated: {}</center>'.format(dt.strftime("%B %d %Y"))

def add_stdout(text):
  return '<div class="code_stdout"><pre>{}</pre></div>'.format(text)

def add_executed_in_seconds(seconds):
  return '<div class="executed_in">(Executed in %.3f seconds.)</div>' % seconds


def generate_code_html(source, info):
  global image_counter
  global animation_counter

  image_name = '"images/image{:03d}.png"'.format(image_counter)
  animation_name = '"animations/animation{:03d}.mp4"'.format(animation_counter)

  execution_before_time = time.time()

  if IMAGE_PNG in source:
    highlighted = highlight(source, PythonLexer(), FORMATTER)
    source = source.replace(IMAGE_PNG, image_name)
    exec (source, globals())

    highlighted += add_executed_in_seconds(time.time() - execution_before_time)

    highlighted += add_image('"../' + image_name[1:], info['width'])
    image_counter += 1
  elif ANIMATION_GIF in source:
    highlighted = highlight(source, PythonLexer(), FORMATTER)
    source = source.replace(ANIMATION_GIF, animation_name)
    exec (source, globals())

    highlighted += add_executed_in_seconds(time.time() - execution_before_time)

    highlighted += add_animation('"../' + animation_name[1:], info['width'])
    animation_counter += 1
  elif PRINT in source:
    highlighted = highlight(source, PythonLexer(), FORMATTER)
    with stdoutIO() as s:
      exec (source, globals())

    highlighted += add_executed_in_seconds(time.time() - execution_before_time)

    highlighted += add_stdout(s.getvalue())

  return highlighted

def generate_pseudo_code(source):
  return "<pre><code>{}</code></pre>".format(source)


def generate_html(template, source_lines):
  body = ''
  for part in partition(template, source_lines):
    if part.tag == HTML_TAG:
      body += part.content
    if part.tag == LAST_UPDATED_TAG:
      body += add_last_updated()
    elif part.tag == CODE_TAG:
      body += generate_code_html(part.content.strip(), part.info)
    elif part.tag == HEADER_TAG:
      body += add_header(part.info['header'])
    elif part.tag == PSEUDO_TAG:
      body += generate_pseudo_code(part.content.strip())

  return template.replace('$BODY', body)


def write_one_file(input_file, output_file, title):
  with open('source/template.data') as f:
    template = f.read()
    template = template.replace('$TITLE', title)

  with open(input_file) as f:
    source = f.readlines()

  output = generate_html(template, source)

  with open(output_file, 'w') as f:
    f.write(output)

def main():
  with open('output/pygments.css', 'w') as f:
    f.write(FORMATTER.get_style_defs('.highlight'))

  input_file = 'source/source0.nomagic'
  output_file = 'output/part0.html'
  title = 'Part 0: Introduction and Notation'

  print('Generating: %s' % title)
  write_one_file(input_file, output_file, title)

  input_file = 'source/source1.nomagic'
  output_file = 'output/part1.html'
  title = 'Part 1: Logistic Regression'

  print('Generating: %s' % title)
  write_one_file(input_file, output_file, title)

  input_file = 'source/source2.nomagic'
  output_file = 'output/part2.html'
  title = 'Part 2: Softmax Regression'

  print('Generating: %s' % title)
  write_one_file(input_file, output_file, title)

  input_file = 'source/source3.nomagic'
  output_file = 'output/part3.html'
  title = 'Part 3: Building a Simple Neural Network'

  # print('Generating: %s' % title)
  # write_one_file(input_file, output_file, title)

main()
