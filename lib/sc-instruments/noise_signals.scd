/*
* Noise signals
*/
[
    SynthDef(\whiteNoiseOsc, {
        arg dur = 1, ampBus = 0, out = 0;
        var noise, amp;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        noise = WhiteNoise.ar(amp);
        Out.ar(out, noise);
    }),

    SynthDef(\pinkNoiseOsc, {
        arg dur = 1, ampBus = 0, out = 0;
        var noise, amp;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        noise = PinkNoise.ar(amp);
        Out.ar(out, noise);
    }),

    SynthDef(\dustOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = Dust.ar(freq, mul:amp);
        Out.ar(out, sig);
    }),

    SynthDef(\lfNoiseOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, lowValue = 0, highValue = 1, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = LFNoise1.ar(freq, mul:amp).range(lowValue, highValue);
        Out.ar(out, sig);
    }),

    SynthDef(\impulseOsc, {
        arg dur = 1, freqBus = 0, ampBus = 0, out = 0;
        var sig, amp, freq;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        freq = In.ar(freqBus, 1);
        sig = Impulse.ar(freq, mul:amp);
        Out.ar(out, sig);
    })
]