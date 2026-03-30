/*
* Filters
*/
[
    SynthDef(\moogFilter, {
        arg dur = 1, in = 0, freqBus = 0, gainBus = 0, out = 0;
        var input, sig, freq, gain;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        gain = In.kr(gainBus, 1);
        sig = MoogFF.ar(input, freq, gain);
        Out.ar(out, sig);
    }),

    SynthDef(\resonantFilter, {
        arg dur = 1, in = 0, freqBus = 0, decayBus = 0, out = 0;
        var input, sig, freq, decay;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        decay = In.ar(decayBus, 1);
        sig = Ringz.ar(input, freq, decay);
        Out.ar(out, sig);
    }),

    SynthDef(\monoHighPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, out = 0;
        var input, sig, freq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        sig = HPF.ar(input, freq);
        Out.ar(out, sig);
    }),

    SynthDef(\stereoHighPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, out = 0;
        var input, sig, freq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 2);
        freq = In.ar(freqBus, 1);
        sig = HPF.ar(input, freq);
        Out.ar(out, sig);
    }),

    SynthDef(\monoLowPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, out = 0;
        var input, sig, freq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        sig = LPF.ar(input, freq);
        Out.ar(out, sig);
    }),

    SynthDef(\stereoLowPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, out = 0;
        var input, sig, freq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 2);
        freq = In.ar(freqBus, 1);
        sig = LPF.ar(input, freq);
        Out.ar(out, sig);
    }),

    SynthDef(\monoBandPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, rqBus = 0, out = 0;
        var input, sig, freq, rq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        rq = In.ar(rqBus, 1);
        sig = BPF.ar(input, freq, rq);
        Out.ar(out, sig);
    }),

    SynthDef(\stereoBandPassFilter, {
        arg dur = 1, in = 0, freqBus = 0, rqBus = 0, out = 0;
        var input, sig, freq, rq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 2);
        freq = In.ar(freqBus, 1);
        rq = In.ar(rqBus, 1);
        sig = BPF.ar(input, freq, rq);
        Out.ar(out, sig);
    }),

    SynthDef(\monoBandRejectFilter, {
        arg dur = 1, in = 0, freqBus = 0, rqBus = 0, out = 0;
        var input, sig, freq, rq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        freq = In.ar(freqBus, 1);
        rq = In.ar(rqBus, 1);
        sig = BRF.ar(input, freq, rq);
        Out.ar(out, sig);
    }),

    SynthDef(\stereoBandRejectFilter, {
        arg dur = 1, in = 0, freqBus = 0, rqBus = 0, out = 0;
        var input, sig, freq, rq;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 2);
        freq = In.ar(freqBus, 1);
        rq = In.ar(rqBus, 1);
        sig = BRF.ar(input, freq, rq);
        Out.ar(out, sig);
    })
]