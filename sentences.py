import struct

class DroneStatusSentenceProcessor:
	# Decodes and prints Drone Status sentences.
	packet_id = -1
	sentence_len = -1
	latitude = -1
	longitude = -1
	altitude = -1
	distance = -1
	fence_alt = -1
	fence_radius = -1
	flight_mode = -1
	voltage = -1
	gps_fix_count = -1
	status1 = -1
	control_signal = -1
	has_data = False # False until we get our first data point.

	def __init__(self, sentence=None):
		# Parse the sentence if we got one.
		if sentence != None:
			self.feed(sentence)

	def feed(self, sentence):
		# I got these byte locations through trial-and-error and reverse
		# engineering the Potensic-M2 Android application.
		self.packet_id = int(sentence[7])
		self.sentence_len = int(sentence[14])
		self.latitude = struct.unpack('i', sentence[16:20])[0] / 10000000
		self.longitude = struct.unpack('i', sentence[20:24])[0] / 10000000
		self.altitude = struct.unpack('h', sentence[24:26])[0]
		self.distance = struct.unpack('h', sentence[26:28])[0]
		self.fence_alt = struct.unpack('h', sentence[28:30])[0]
		self.fence_distance = struct.unpack('h', sentence[30:32])[0]
		self.fence_radius = int(sentence[32])
		self.flight_mode = int(sentence[33])
		self.voltage = int(sentence[34]) / 10
		self.gps_fix_count = int(sentence[35])
		self.status1 = int(sentence[36])
		self.control_signal = int(sentence[37])
		self.has_data = True

	def flight_mode_str(self):
		# Convert the flight_mode variable to a descriptive string.
		if self.flight_mode == 0:
			return "         grounded"
		if self.flight_mode == 1:
			return "    manual flight"
		if self.flight_mode == 2:
			return "gps-assist flight"
		return f"unknown: {self.flight_mode}"

	def print_pretty(self):
		# Print one line of status information.
		if self.has_data:
			print(f"{self.packet_id:3} | lat: {self.latitude:3.7f}, lon: {self.longitude:3.7f}, alt: {self.altitude:3}m, dist: {self.distance:4}m, fm: {self.flight_mode_str():17}, bat: {self.voltage}V")
		else:
			print("No data available!")

class CameraStatusSentenceProcessor():
	# Decodes and prints Camera sentences. Handles both photo and video sentences.
	status = ""

	def __init__(self, is_video = False, sentence=None):
		# Parse the sentence if we got one.
		if sentence != None:
			self.feed(is_video, sentence)

	def feed(self, is_video, sentence):
		# Decode the sentence. These sentences are pretty simple, with just a
		# string field describing the operation.
		self.packet_id = int(sentence[7])
		self.status = str(sentence [12:].decode("utf-8"))

	def print_pretty(self):
		# TODO: handle any error codes that we might receive.
		# I haven't seen any errors during my flights, but it *could*
		# happen and would result in a "Camera status unknown" error here.
		#
		# TODO: properly handle video start vs. video end. This difficult
		# because we appear to get the same message for start and end events,
		# and I would really like to avoid local state in this program (it
		# could cause desyncs if we lose packets, which is very possible when
		# using UDP over a wireless link to a drone).
		if self.status == "": # This should never happen.
			print("No data available!")
		elif self.status == "SNAP_OK": # Received when the drone successfully takes a picture.
			print(f"{self.packet_id:3} | Picture OK.")
		elif self.status == "REC_OK": # Received when the drone starts or ends a video.
			print(f"{self.packet_id:3} | Record OK.")
		else:
			print("Camera status unknown!")
