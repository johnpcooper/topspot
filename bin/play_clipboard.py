from spotify_jpc import playback, utilities

def run():

	utilities.set_env_vars()
	playback.play_clipboard()

if __name__ == "__main__":
	run()