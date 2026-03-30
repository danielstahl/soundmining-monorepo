/*
* Signal combination
*/

[
    SynthDef(\signalMix, {
        arg dur = 1, in1 = 0, in2 = 0, out = 0;
        var sig1, sig2, result;
        Line.kr(dur:dur, doneAction:2);
        sig1 = In.ar(in1, 1);
        sig2 = In.ar(in2, 1);
        result = Mix.new([sig1, sig2]);
        Out.ar(out, result);
    }),

    SynthDef(\signalMultiply, {
        arg dur = 1, in1 = 0, in2 = 0, out = 0;
        var sig1, sig2, result;
        Line.kr(dur:dur, doneAction:2);
        sig1 = In.ar(in1, 1);
        sig2 = In.ar(in2, 1);
        result = sig1 * sig2;
        Out.ar(out, result);
    }),

    SynthDef(\signalSum, {
        arg dur = 1, in1 = 0, in2 = 0, out = 0;
        var sig1, sig2, result;
        Line.kr(dur:dur, doneAction:2);
        sig1 = In.ar(in1, 1);
        sig2 = In.ar(in2, 1);
        result = sig1 + sig2;
        Out.ar(out, result);
    }),

    SynthDef(\signalShape, {
        arg dur = 1, in = 0, shapeBus = 0, out = 0;
        var sig, shape, result;
        Line.kr(dur:dur, doneAction:2);
        sig = In.ar(in, 1);
        shape = In.ar(shapeBus, 1);
        result = sig.lincurve(-1, 1, -1, 1, shape);
        Out.ar(out, result);
    })
]