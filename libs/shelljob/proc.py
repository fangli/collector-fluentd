# Subprocess containers
"""
	A mechanism to run subprocesses asynchronously and with non-blocking read.
"""
import os
import atexit
import Queue
import shlex
import subprocess
import threading

class Group:
	"""
		Runs a subprocess in parallel, capturing it's output and providing non-blocking reads (well, at
		least for the caller they appear non-blocking).
	"""
	def __init__(self):
		self.output = Queue.Queue()
		self.handles = []
		self.waiting = 0
		
	def run( self, cmd, shell = False ):
		"""
			Adds a new process to this object. This process is run and the output collected.
			
			@param cmd: the command to execute. This may be an array as passed to Popen,
				or a string, which will be parsed by 'shlex.split'
			@return: the handle to the process return from Popen
		"""
		cmd = _expand_cmd(cmd)

		handle = subprocess.Popen( cmd,
			shell = shell,
			bufsize = 1,
			stdout = subprocess.PIPE,
			stderr = open(os.devnull, 'wb'),
			stdin = subprocess.PIPE, # needed to detach from calling terminal (other wacky things can happen)
			preexec_fn=os.setsid,
		)
		handle.group_output_done = False
		self.handles.append( handle )
		
		# a thread is created to do blocking-read
		self.waiting += 1
		def block_read():
			try:
				for line in iter( handle.stdout.readline, '' ):
					self.output.put( ( handle, line ) )
			except:
				pass
				
			# To force return of any waiting read (and indicate this process is done
			self.output.put( ( handle, None ) )
			handle.stdout.close()
			self.waiting -= 1
			
		block_thread = threading.Thread( target = block_read )
		block_thread.daemon = True
		block_thread.start()
			
		# kill child when parent dies
		def premature_exit():
			try: 
				handle.terminate()
			except:
				pass # who cares why, we're exiting anyway (most likely since it is already terminated)
		atexit.register( premature_exit )
			
		return handle
		
	def readlines( self, max_lines = 1000,  timeout = 2.0 ):
		"""
			Reads available lines from any of the running processes. If no lines are available now
			it will wait until 'timeout' to read a line. If nothing is running the timeout is not waited
			and the function simply returns.
			
			When a process has been completed and all output has been read from it, a
			variable 'group_ouput_done' will be set to True on the process handle.
			
			@param timeout: how long to wait if there is nothing available now
			@param max_lines: maximum number of lines to get at once
			@return: An array of tuples of the form:
				( handle, line )
				There 'handle' was returned by 'run' and 'line' is the line which is read.
				If no line is available an empty list is returned.
		"""
		lines = []
		try:
			while len(lines) < max_lines:
				handle, line = self.output.get_nowait()
				# interrupt waiting if nothing more is expected
				if line == None:
					handle.group_output_done = True
					if self.waiting == 0:
						break
				else:
					lines.append( ( handle, line ) )
			return lines
			
		except Queue.Empty:
			# if nothing yet, then wait for something
			if len(lines) > 0 or self.waiting == 0:
				return lines
			
			item = self.readline( timeout = timeout )
			if item != None:
				lines.append( item )
			return lines
			
	def readline( self, timeout = 2.0 ):
		"""
			Read a single line from any running process.
			
			Note that this will end up blocking for timeout once all processes have completed.
			'readlines' however can properly handle that situation and stop reading once
			everything is complete.
			
			@return: Tuple of ( handle, line ) or None if no output generated.
		"""
		try:
			handle, line = self.output.get( timeout = timeout )
			if line == None:
				handle.group_output_done = True
				return None
			return (handle, line)
		except Queue.Empty:
			return None

	def is_pending( self ):
		"""
			Determine if calling readlines would actually yield any output. This returns true
			if there is a process running or there is data in the queue.
		"""
		if self.waiting > 0:
			return True
		return not self.output.empty()
		
	def count_running( self ):
		"""
			Return the number of processes still running. Note that although a process may
			be finished there could still be output from it in the queue. You should use 'is_pending'
			to determine if you should still be reading.
		"""
		count = 0
		for handle in self.handles:
			if handle.poll() == None:
				count += 1
		return count
		
	def get_exit_codes( self ):
		"""
			Return a list of all processes and their exit code.
			
			@return: A list of tuples:
				( handle, exit_code )
				'handle' as returned from 'run'
				'exit_code' of the process or None if it has not yet finished
		"""
		codes = []
		for handle in self.handles:
			codes.append( ( handle, handle.poll() ) )
		return codes
		
	def clear_finished( self ):
		"""
			Remove all finished processes from the managed list.
		"""
		nhandles = []
		for handle in self.handles:
			if not handle.group_output_done or handle.poll() == None:
				nhandles.append( handle )
		self.handles = nhandles


class BadExitCode(Exception):
	def __init__(self, exit_code, output):
		Exception.__init__( self, 'subprocess-bad-exit-code' )
		self.exit_code = exit_code
		self.output = output
	
class Timeout(Exception):
	def __init__(self, output):
		Exception.__init__( self, 'subprocess-timeout' )
		self.output = output
		
def call( cmd, encoding = 'utf-8', shell = False, check_exit_code = True, timeout = None ):
	"""
		Calls a subprocess and returns the output and optionally exit code.
		
		@param encoding: convert output to unicode objects with this encoding, set to None to
			get the raw output
		@param check_exit_code: set to False to ignore the exit code, otherwise any non-zero
			result will throw BadExitCode.
		@param timeout: If specified only this amount of time (seconds) will be waited for
			the subprocess to return
		@return: If check_exit_code is False: list( output, exit_code ), else just the output
	"""
	cmd = _expand_cmd(cmd)
	proc = subprocess.Popen( cmd, stdout = subprocess.PIPE, stderr = open(os.devnull, 'wb'),
		stdin = subprocess.PIPE, shell = shell, preexec_fn=os.setsid )

	def decode(out):
		if encoding != None:
			return unicode( out, encoding )
		else:
			return raw_out
	
	if timeout == None:
		raw_out, ignore_err = proc.communicate()
	else:
		# Read from subprocess in a thread so the main one can check for the timeout
		outq = Queue.Queue()
		def block_read():
			# collect as lines so if timeout we still have partial output
			out = proc.stdout.read()
			outq.put( out )
			
		block_thread = threading.Thread( target = block_read )
		block_thread.daemon = True
		block_thread.start()

		try:
			raw_out = outq.get(True,timeout)
		except Queue.Empty:
			proc.terminate()
			# wait again for partial output (process is terminated, so reading should end)
			raw_out = outq.get()
			raise Timeout( decode(raw_out) )
	
	out = decode(raw_out)
	exit_code = proc.poll()
	
	if check_exit_code:
		if exit_code != 0:
			raise BadExitCode( exit_code, out )
		return out
		
	return ( out, proc.poll() )
	
def _expand_cmd(cmd):
	if isinstance(cmd, basestring):
		cmd = shlex.split(cmd)
	return cmd
	
