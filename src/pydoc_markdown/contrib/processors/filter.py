# -*- coding: utf8 -*-
# Copyright (c) 2019 Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

"""
Provides a processor that implements various filter capabilities.
"""

from nr.types.interface import implements
from nr.types.structured import Field, Object
from pydoc_markdown.interfaces import Processor


class FilterProcessorConfiguration(Object):
  expression = Field(str, default=None)
  documented_only = Field(bool, default=False)
  exclude_private = Field(bool, default=True)
  exclude_special = Field(bool, default=True)


@implements(Processor)
class FilterProcessor(object):
  """
  The `filter` processor removes module and class members based on certain
  criteria.

  # Example

  ```py
  - type: filter
    expression: not name.startswith('_') and default()
  ```
  """

  CONFIG_CLASS = FilterProcessorConfiguration

  def process(self, config, graph):
    graph.visit(lambda x: self._process_member(config, x), allow_mutation=True)

  def _process_member(self, config, node):
    def default_check():
      if config.documented_only and not node.docstring:
        return False
      if config.exclude_private and node.name.startswith('_') and not node.name.endswith('_'):
        return False
      if config.exclude_special and node.name in ('__path__', '__annotations__', '__name__', '__all__'):
        return False
      return True

    if config.expression:
      scope = {'name': node.name, 'node': node, 'default': default_check}
      if not eval(config.expression, scope):
        node.remove()
    if node.parent and not default_check():
      node.remove()
