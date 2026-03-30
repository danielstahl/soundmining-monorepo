/*
* Modulate volume of signal
*/
[
    SynthDef(\monoVolume, {
        arg dur = 1, in = 0, out = 0, ampBus = 0;
        var input, amp;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        input = In.ar(in, 1);

        Out.ar(out, input * amp);
    }),

    SynthDef(\stereoVolume, {
        arg dur = 1, in = 0, out = 0, ampBus = 0;
        var input, amp;
        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        input = In.ar(in, 2);

        Out.ar(out, input * amp);
    })
]