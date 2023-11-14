# work_balance_control
 Emergency care when you can't take a break to stay healthy

 ## Usage
 Ajust the settings in the ini-file and just run "work_balance_control.pyw" (if the program has started  successfully, you will hear a beep sound)

 At a suitable time, a dialog box will appear requesting you to interrupt your work and go for a rest. You can postpone a certain number of times for a given time, but you cannot do it any more.

 ![GUI](/images/work_balance_control.png)

 ## Examples
 All program settings are stored in the ini-file and allow you to fine-tune the rest-work balance:
 ```ini
 [COMMON]
 # work time until first rest (minutes)
 work_duration = 45
 # increment of working time until the next rest (minutes)
 work_delta = -5
 # first rest time (minutes)
 relax_duration = 5
 # increment of subsequent rest time (minutes)
 relax_delta = 5
 # audible warning before the next rest (minutes)
 relax_warning = 5
 # maximum allowable clean work time (minutes)
 maximum_work_time = 240
 # maximum allowable total time, work and rest (minutes)
 maximum_time = 240
 # allowable interruption interval of current rest (minutes)
 interrupt_pause = 2

 [NOTIFIERS]
 # notification sound when rest starts
 sound_relax_begin=begin.mp3
 # sound to notify you when the rest has stopped
 sound_relax_end=end.mp3
 # notification sound for the next resting period
 sound_relax_warning=warning.mp3

 [SYSTEM]
 # clock frequency (60 defaults to 1 minute)
 timer_clock_cycle = 60
 # force locking the screen while resting
 force_lock = True
 # display the status of the current rest in fullscreen mode
 fullscreen = True
 # display the current resting state on top of all windows
 topmost = True
 ```

 ## Remarks
 This software works correctly with full functionality only under OS Windows. Be careful with the combination of setting parameters "force_lock = True + fullscreen = True + topmost = True" (default) -- this is the most efficient solution, but with incorrectly configured timings you may lose unsaved data due to the need to restart the PC. If you want to quickly test your parameters, temporarily change the parameter "timer_clock_cycle"  (for example, a value of 6 will speed up the timer by a factor of 10 instead of the default 60).
