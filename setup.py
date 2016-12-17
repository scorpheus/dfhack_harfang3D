import sys
from cx_Freeze import setup, Executable


# Gather extra runtime dependencies.
def gather_extra_redist():
	import os
	import gs
	import inspect

	path = os.path.dirname(inspect.getfile(gs))
	files = os.listdir(path)

	out = []
	for file in files:
		name, ext = os.path.splitext(file)
		if ext in ['.dll', '.so'] and "Debug" not in name:
			out.append(os.path.join(path, file))

	return out


extra_redist = gather_extra_redist()

# Dependencies are automatically detected, but it might need fine tuning.
options = {
	'build_exe': {
		'build_exe': 'build',
		'no_compress': False,
		'packages': ['gs'],
		'include_files': ['assets/', 'environment_kit/', 'environment_kit_inca/', 'minecraft_assets/'] + extra_redist
	}
}

setup(  name = "DwarfVision",
		version = "1.0",
		description = "DwarfVision",
		options = options,
		executables = [Executable("main.py")])
