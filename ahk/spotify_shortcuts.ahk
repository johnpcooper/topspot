; Use topspot to search spotify for whatever's on the clipboard and, if any tracks show
; up in results, play the first one. Won't work if spotify isn't active on a device

; This is a good example of how to activate an environment and then run a function from a
; package that's installed in that environment using AHK.

; This way, I can just script like in Ipython in working environment
^!1::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot import playback; playback.play_clipboard()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return

; Add first track in search results for cliboard to
; queue. 
^!2::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot.playback import add_clipboard_to_queue; add_clipboard_to_queue()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return

; Add currently playing track to the singles playlist
; corresponding to its release date
^!3::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot.playlist import add_current_track_to_playlist; add_current_track_to_playlist()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return

; Seeking forward and reverse
!+]::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot.playback import seek_for; seek_for()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return

!+[::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot.playback import seek_rev; seek_rev()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return

; Skip to the last 0.1 percent of the currently playing track
; so that we can skip it but still have it get recorden in
; recently played.
!\::

  env = C:\.topspot\Scripts\activate
  pycommand := "from topspot.playback import pseudoskip; pseudoskip()"
  run, %comspec% /c %env% & python -c "%pycommand%"

return