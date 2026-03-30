/*
* Deterministic signals.
*/
[
    SynthDef(\sineOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = SinOsc.ar(freq, mul:amp);
        Out.ar(out, sig);
    }),

    SynthDef(\sawOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = LFSaw.ar(freq, mul:amp);
        Out.ar(out, sig);
    }),

    SynthDef(\triangleOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = LFTri.ar(freq, mul:amp);
        Out.ar(out, sig);
    }),

    SynthDef(\pulseOsc, {
        arg dur = 1, freqBus = 0, widthBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq, width;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        width = In.ar(widthBus, 1);
        sig = Pulse.ar(freq, width:width, mul:amp);
        Out.ar(out, sig);
    })
]