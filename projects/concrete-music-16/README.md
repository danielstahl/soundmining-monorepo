# TBD - concrete-music-16

Same sounds as concrete-music-15. Perhaps two or threee 
contrasting sounds. 

Granular synthesis. Perhpas in combination with fm-synthesis.

Filter sounds in lo-fi. First with a radio sound that pass sounds
between 500 - 2500 Hz.

```Python
filtered = (
    piece.synth_player
    .note()
    .sound_mono("your_sound", 1.0, static_control(1.0))
    .mono_high_pass_filter(static_control(500))  # cut the low end
    .mono_low_pass_filter(static_control(3500))  # cut the high end
    .pan(static_control(0))
    .play(start_time=start)
)
```

Then a more muffled sound. Through a wall or perhaps underwater. Through 
the wall is an low pass at about 200-500 Hz and underwater is about 500-1000 Hz

```Python
wall_muffled = (
    piece.synth_player
    .note()
    .sound_mono("your_sound", 1.0, static_control(1.0))
    .mono_low_pass_filter(static_control(300))
    .pan(static_control(0))
    .play(start_time=start)
)
```



