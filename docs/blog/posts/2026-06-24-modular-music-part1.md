---
date: 2026-05-24
authors: [daniel]
title: Modular Music Part 1
categories:
    - Music
tags:
    - supercollider
    - modular-music
description: How I use do modular sythesis in SuperCollider.
image: https://danielstahl.github.io/soundmining-monorepo/assets/header-social-card.jpeg
---

# Modular Music Part 1
*This Post was originally published on my blog 2022-06-07*

I use [Supercollider](https://supercollider.github.io/) to make music. Here I will briefly describe how Supercollider works and are used to generate and work with audio.

It has two parts. A client, with its own programming language. And a server that receives command too, for instance, play a sound on an instrument.  One way to work is too create instruments in the server that combines a number of so called UGens. You can then send commands to the server that will play these instruments on the server. 

One common problem that arise when working with instruments is that It is hard to make these instruments generic enough so that they are re-usable. If you for instance play a sine tone you sometimes want to make one note and some other times a glissando. You might also want to have different dynamic curves at different times. You quickly end up in a combination hell and need a lot of different instrument where there is very little difference. 

Modular synthesis and sound systems has been around for many years. From the early Moog synths to the euro rack system. Also in pure software we have everything from Max to the open source PureData. The main idea is that you control modules by sending one or several signals to them. Each module transform the incoming signals and produce a new outgoing signal. You use that signal to either control other modules or output it as the final sound. It is an elegant and versatile solution.

One way to communicate between instruments in Supercollider is via something called buses. Buses are a way to stream data. Buses come in either control rate buses or audio rate buses. Control rate buses have a lower rate than audio buses and are used to transport control information such as volume changes. Most audio buses are internal, meaning that no sound will come out if you send data to them, they are used for internal routing. You specify how many external audio buses you should have, two is typical to get stereo with left and right.

In my modular system I use buses to communicate between different instruments. I have both instruments that produce control signals such as a static value or going from one value to another in a line. And instruments that produce audio rate signals such as sine signals and filters. Below is an example of a control signal instrument that produces a signal going from one value to another.

```supercollider
SynthDef(\lineControl, {
	arg dur = 1, startValue = 1, endValue = 1, out = 0;
	var lineEnv;
	lineEnv = Line.ar(start: startValue, 
                          end: endValue, 
                          dur: dur, doneAction:2);
	Out.ar(out, lineEnv);
}).add;
```

The above instruments takes four arguments. The `dur` means how long the instrument should sound, `out` means which output bus the instrument should send the result to and start/end-value is the start and end value of the produced values. The Out.ar send the values on the specified bus. By using ar it sends it at audio rate.

You can later use this instrument to control other instruments. Below is an example of a sine instrument that reads both its frequency and amplitude from a control bus.

```supercollider
SynthDef(\sineOsc, {
	arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
	var sig, amp, freq;
	Line.kar(dur:dur, doneAction:2);
	amp = In.ar(ampBus, 1);
	freq = In.ar(freqBus, 1);
	sig = SinOsc.ar(freq, mul:amp);
	Out.ar(out, sig);
}).add;
```

This instrument takes it frequency from freqBus and the amplitude from the ampBus. The In.ar reads from a bus (at audio rate). As before it sends the result to the output bus with Out.ar. 

I have a lot of Supercollider instruments that I use to make music. They reflect my needs as a composer and is not a “complete” set of instruments.

There are a number of control instruments. Both simple, such as the above lineControl, and instruments that combines several buses such as multiply, sum and mix.
To be able to combine instruments in a more dynamic way. e.g a line control with a sine wave, all instruments are at audio rate. 

Many audio instruments are also simple such as sine, triangle and noise. There are also modifying and more complex instruments such as filters, ring modulation and FM modulation.

For working with samples there are sample playback instruments. One special control instrument is an audio amplitude control instrument that takes an audio signal and outputs a control signal from amplitude. This is useful if you for instance want to do a sub base.

You can use the Supercollider client to combine these instruments and play them but it can be a bit of a hassle to do. Especially to manage the buses that you use. I play these Supercollider instruments from a different environment that I will describe in a future post.

