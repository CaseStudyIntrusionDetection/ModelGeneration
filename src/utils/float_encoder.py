import json
import numpy

# export to file
class FloatEncoder(json.JSONEncoder):
	"""Custom JSONEncoder class for JSON serialization.

	"""

	def default(self, obj):
		"""The default encoding functionality.

			Args:
				obj (any): The object to encode.
			
			Returns:
				(any): The encoded object.
		"""
		if isinstance(obj, numpy.integer):
			return int(obj)
		elif isinstance(obj, numpy.floating):
			return float(obj)
		elif isinstance(obj, numpy.ndarray):
			return obj.tolist()
		else:
			return super(FloatEncoder, self).default(obj)