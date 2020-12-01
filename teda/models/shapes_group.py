import colorsys
import os
from random import random

from traitlets import HasTraits, Unicode, Int, Bool

from astwro.starlist import StarList

class ShapesGroup(HasTraits):
	""" This class optionally tracks StarList corresponding to group of shapes"""
	name = Unicode('unnamed')
	file = Unicode(allow_none=True)
	color = Unicode('r')
	count = Int()
	modified = Bool(default_value=False)

	def __init__(self, starlist = None):
		super().__init__()
		self.starlist:StarList = starlist
		self.color = "#{:02x}{:02x}{:02x}".format(*(int(255*c) for c in colorsys.hls_to_rgb(random(), 0.6, random()/2.0 + 0.5)))
		self._next_id = None

	def on_shape_moved(self, x, y, id):
		if self.starlist is None:
			return

		self.starlist.at[id, 'x'] = x
		self.starlist.at[id, 'y'] = y
		self.modified = True

	def on_shape_added(self, x, y, label=None):
		if self.starlist is None:
			self.count += 1
			return self.count if label is None else label

		from pandas import Series
		if label is None:
			label = self._new_id()
		if label not in self.starlist.index:
			self.starlist.append(Series({'id': label, 'x': x, 'y': y}, name=label))
			self.count = self.starlist.stars_number()
			self.modified = True
		return label

	def on_shape_deleted(self, id):
		if self.starlist is None:
			self.count -= 1
			return
		try:
			self.starlist.drop(id)
			self.modified = True
			self.count = self.starlist.stars_number()
		except :
			print("Error in on_shape_deleted") # to do

	def read_file(self, filename):
		ext = os.path.splitext(filename)[1]
		if ext.lower() == '.reg':
			return self.read_ds9_regions(filename)
		else:
			return self.read_daophot_file(filename)

	def write_file(self, filename, overwrite=True):
		ext = os.path.splitext(filename)[1]
		if ext.lower() == '.reg':
			self.write_ds9_regions(filename, overwrite=overwrite)
		else:
			self.write_daophot_file(filename, overwrite=overwrite)

	def read_ds9_regions(self, filename):
		from astwro.starlist import read_ds9_regions
		self.starlist = read_ds9_regions(filename)
		self.count = self.starlist.stars_number()
		self.modified = False
		return self.starlist

	def read_daophot_file(self, filename):
		from astwro.starlist import read_dao_file
		self.starlist = read_dao_file(filename)
		self.count = self.starlist.stars_number()
		self.modified = False
		return self.starlist

	def write_ds9_regions(self, filename, overwrite=True):
		from astwro.starlist import write_ds9_regions
		write_ds9_regions(filename, color=None)   # color?
		self.modified = False

	def write_daophot_file(self, filename, overwrite=True):
		from astwro.starlist import write_ds9_regions
		write_ds9_regions(filename, color=None)   # color?
		self.modified = False

	def _new_id(self):
		if self._next_id is None:
			# some heuristic -  start new thousand
			self._next_id = (self.starlist.index.max() // 1000 + 1) * 1000
		self._next_id += 1
		return self._next_id - 1

