import unittest
import pandas.tools.rplot as rplot
from pandas import read_csv
import os
import matplotlib.pyplot as plt
import pdb

def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth

def between(a, b, x):
	"""Check if x is in the somewhere between a and b.

	Parameters:
	-----------
	a: float, interval start
	b: float, interval end
	x: float, value to test for

	Returns:
	--------
	True if x is between a and b, False otherwise
	"""
	if a < b:
		return x >= a and x <= b
	else:
		return x <= a and x >= b

class TestUtilityFunctions(unittest.TestCase):
	"""
	Tests for RPlot utility functions.
	"""
	def setUp(self):
		path = os.path.join(curpath(), 'data/iris.csv')
		self.data = read_csv(path, sep=',')

	def test_make_aes1(self):
		aes = rplot.make_aes()
		self.assertTrue(aes['x'] is None)
		self.assertTrue(aes['y'] is None)
		self.assertTrue(aes['size'] is None)
		self.assertTrue(aes['colour'] is None)
		self.assertTrue(aes['shape'] is None)
		self.assertTrue(aes['alpha'] is None)
		self.assertTrue(type(aes) is dict)

	def test_make_aes2(self):
		with self.assertRaises(ValueError):
			rplot.make_aes(size=rplot.ScaleShape('test'))
		with self.assertRaises(ValueError):
			rplot.make_aes(colour=rplot.ScaleShape('test'))
		with self.assertRaises(ValueError):
			rplot.make_aes(shape=rplot.ScaleSize('test'))
		with self.assertRaises(ValueError):
			rplot.make_aes(alpha=rplot.ScaleShape('test'))

	def test_dictionary_union(self):
		dict1 = {1 : 1, 2 : 2, 3 : 3}
		dict2 = {1 : 1, 2 : 2, 4 : 4}
		union = rplot.dictionary_union(dict1, dict2)
		self.assertEqual(len(union), 4)
		keys = union.keys()
		self.assertTrue(1 in keys)
		self.assertTrue(2 in keys)
		self.assertTrue(3 in keys)
		self.assertTrue(4 in keys)
		self.assertTrue(rplot.dictionary_union(dict1, {}) == dict1)
		self.assertTrue(rplot.dictionary_union({}, dict1) == dict1)
		self.assertTrue(rplot.dictionary_union({}, {}) == {})

	def test_merge_aes(self):
		layer1 = rplot.Layer(size=rplot.ScaleSize('test'))
		layer2 = rplot.Layer(shape=rplot.ScaleShape('test'))
		rplot.merge_aes(layer1, layer2)
		self.assertTrue(isinstance(layer2.aes['size'], rplot.ScaleSize))
		self.assertTrue(isinstance(layer2.aes['shape'], rplot.ScaleShape))
		self.assertTrue(layer2.aes['size'] == layer1.aes['size'])
		for key in layer2.aes.keys():
			if key != 'size' and key != 'shape':
				self.assertTrue(layer2.aes[key] is None)

	def test_sequence_layers(self):
		layer1 = rplot.Layer(self.data)
		layer2 = rplot.GeomPoint(x='SepalLength', y='SepalWidth', size=rplot.ScaleSize('PetalLength'))
		layer3 = rplot.GeomPolyFit(2)
		result = rplot.sequence_layers([layer1, layer2, layer3])
		self.assertEqual(len(result), 3)
		last = result[-1]
		self.assertEqual(last.aes['x'], 'SepalLength')
		self.assertEqual(last.aes['y'], 'SepalWidth')
		self.assertTrue(isinstance(last.aes['size'], rplot.ScaleSize))
		self.assertTrue(self.data is last.data)
		self.assertTrue(rplot.sequence_layers([layer1])[0] is layer1)

class TestTrellis(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/tips.csv')
		self.data = read_csv(path, sep=',')
		layer1 = rplot.Layer(self.data)
		layer2 = rplot.GeomPoint(x='total_bill', y='tip')
		layer3 = rplot.GeomPolyFit(2)
		self.layers = rplot.sequence_layers([layer1, layer2, layer3])
		self.trellis1 = rplot.TrellisGrid(['sex', 'smoker'])
		self.trellis2 = rplot.TrellisGrid(['sex', '.'])
		self.trellis3 = rplot.TrellisGrid(['.', 'smoker'])
		self.trellised1 = self.trellis1.trellis(self.layers)
		self.trellised2 = self.trellis2.trellis(self.layers)
		self.trellised3 = self.trellis3.trellis(self.layers)

	def test_grid_sizes(self):
		self.assertEqual(len(self.trellised1), 3)
		self.assertEqual(len(self.trellised2), 3)
		self.assertEqual(len(self.trellised3), 3)
		self.assertEqual(len(self.trellised1[0]), 2)
		self.assertEqual(len(self.trellised1[0][0]), 2)
		self.assertEqual(len(self.trellised2[0]), 2)
		self.assertEqual(len(self.trellised2[0][0]), 1)
		self.assertEqual(len(self.trellised3[0]), 1)
		self.assertEqual(len(self.trellised3[0][0]), 2)
		self.assertEqual(len(self.trellised1[1]), 2)
		self.assertEqual(len(self.trellised1[1][0]), 2)
		self.assertEqual(len(self.trellised2[1]), 2)
		self.assertEqual(len(self.trellised2[1][0]), 1)
		self.assertEqual(len(self.trellised3[1]), 1)
		self.assertEqual(len(self.trellised3[1][0]), 2)
		self.assertEqual(len(self.trellised1[2]), 2)
		self.assertEqual(len(self.trellised1[2][0]), 2)
		self.assertEqual(len(self.trellised2[2]), 2)
		self.assertEqual(len(self.trellised2[2][0]), 1)
		self.assertEqual(len(self.trellised3[2]), 1)
		self.assertEqual(len(self.trellised3[2][0]), 2)

	def test_trellis_cols_rows(self):
		self.assertEqual(self.trellis1.cols, 2)
		self.assertEqual(self.trellis1.rows, 2)
		self.assertEqual(self.trellis2.cols, 1)
		self.assertEqual(self.trellis2.rows, 2)
		self.assertEqual(self.trellis3.cols, 2)
		self.assertEqual(self.trellis3.rows, 1)

class TestScaleGradient(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/iris.csv')
		self.data = read_csv(path, sep=',')
		self.gradient = rplot.ScaleGradient("SepalLength", colour1=(0.2, 0.3, 0.4), colour2=(0.8, 0.7, 0.6))

	def test_gradient(self):
		for index in range(len(self.data)):
			row = self.data.irow(index)
			r, g, b = self.gradient(self.data, index)
			r1, g1, b1 = self.gradient.colour1
			r2, g2, b2 = self.gradient.colour2
			self.assertTrue(between(r1, r2, r))
			self.assertTrue(between(g1, g2, g))
			self.assertTrue(between(b1, b2, b))

class TestScaleGradient2(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/iris.csv')
		self.data = read_csv(path, sep=',')
		self.gradient = rplot.ScaleGradient2("SepalLength", colour1=(0.2, 0.3, 0.4), colour2=(0.8, 0.7, 0.6), colour3=(0.5, 0.5, 0.5))

	def test_gradient2(self):
		for index in range(len(self.data)):
			row = self.data.irow(index)
			r, g, b = self.gradient(self.data, index)
			r1, g1, b1 = self.gradient.colour1
			r2, g2, b2 = self.gradient.colour2
			r3, g3, b3 = self.gradient.colour3
			value = row[self.gradient.column]
			a_ = min(self.data[self.gradient.column])
			b_ = max(self.data[self.gradient.column])
			scaled = (value - a_) / (b_ - a_)
			if scaled < 0.5:
				self.assertTrue(between(r1, r2, r))
				self.assertTrue(between(g1, g2, g))
				self.assertTrue(between(b1, b2, b))
			else:
				self.assertTrue(between(r2, r3, r))
				self.assertTrue(between(g2, g3, g))
				self.assertTrue(between(b2, b3, b))

class TestScaleRandomColour(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/iris.csv')
		self.data = read_csv(path, sep=',')
		self.colour = rplot.ScaleRandomColour('SepalLength')

	def test_random_colour(self):
		for index in range(len(self.data)):
			colour = self.colour(self.data, index)
			self.assertEqual(len(colour), 3)
			r, g, b = colour
			self.assertGreaterEqual(r, 0.0)
			self.assertGreaterEqual(g, 0.0)			
			self.assertGreaterEqual(b, 0.0)			
			self.assertLessEqual(r, 1.0)
			self.assertLessEqual(g, 1.0)
			self.assertLessEqual(b, 1.0)

class TestScaleConstant(unittest.TestCase):
	def test_scale_constant(self):
		scale = rplot.ScaleConstant(1.0)
		self.assertEqual(scale(None, None), 1.0)
		scale = rplot.ScaleConstant("test")
		self.assertEqual(scale(None, None), "test")

class TestScaleSize(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/iris.csv')
		self.data = read_csv(path, sep=',')
		self.scale1 = rplot.ScaleShape('Name')
		self.scale2 = rplot.ScaleShape('PetalLength')

	def test_scale_size(self):
		for index in range(len(self.data)):
			marker = self.scale1(self.data, index)
			self.assertTrue(marker in ['o', '+', 's', '*', '^', '<', '>', 'v', '|', 'x'])

	def test_scale_overflow(self):
		with self.assertRaises(ValueError):
			for index in range(len(self.data)):
				self.scale2(self.data, index)

class TestRPlot1(unittest.TestCase):
	def setUp(self):
		path = os.path.join(curpath(), 'data/tips.csv')
		self.data = read_csv(path, sep=',')
		self.plot = rplot.RPlot(self.data, x='tip', y='total_bill')
		self.plot + rplot.TrellisGrid(['sex', 'smoker'])
		self.plot + rplot.GeomPoint(colour=rplot.ScaleRandomColour('day'), shape=rplot.ScaleShape('size'))
		self.fig = plt.gcf()
		self.plot.render(self.fig)
		pdb.set_trace()

	def test_subplots(self):
		self.assertEqual(len(self.fig.axes), 4)

if __name__ == '__main__':
	unittest.main()