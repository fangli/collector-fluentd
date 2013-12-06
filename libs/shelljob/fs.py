"""
	A collection of filesystem related commands.
"""
import os, re

def find( path, 
	include_dirs = True, include_files = True,
	name_regex = None, not_name_regex = None,
	whole_name_regex = None, not_whole_name_regex = None,
	exclude_root = False ):
	"""
		Creates an iterator of files matching a variety of conditions.
		
		@param path: which path to iterate
		@param include_dirs: include directories in output
		@param include_files: include files in output
		@param name_regex: optional regex string compared against basename of file
		@param not_name_regex: if specificed only produces names not matching this regex
		@param whole_name_regex: like name_regex but applies to whole path, not just basename
		@param not_whole_name_regex: like not_name_regex but applies to whole path
		@param exclude_root: do not include the intput 'path' itself in the output
		@return: a generator for the matched files
	"""
	def maybe_regex(arg):
		return re.compile(arg) if arg != None else None
	c_name_regex = maybe_regex(name_regex)
	c_not_name_regex = maybe_regex(not_name_regex)
	c_whole_name_regex = maybe_regex(whole_name_regex)
	c_not_whole_name_regex = maybe_regex(not_whole_name_regex)
	
	def check_name(name, whole_name):
		if c_name_regex != None and not c_name_regex.match( name ):
			return False
		if c_not_name_regex != None and c_not_name_regex.match( name ):
			return False
		if c_whole_name_regex != None and not c_whole_name_regex.match( whole_name ):
			return False
		if c_not_whole_name_regex != None and c_not_whole_name_regex.match( whole_name ):
			return False
		return True
		
	walker = os.walk( path, followlinks = True )
	def filter_func():
		for root, dirs, files in walker:
			if root == path and exclude_root:
				pass
			elif include_dirs and check_name( os.path.basename(root), root ):
				yield root
				
			if include_files:
				for item in files:
					whole = os.path.join( root, item )
					if check_name( item, whole ):
						yield whole
	
	return filter_func()
