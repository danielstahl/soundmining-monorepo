/*
* Pan
*/
[
    SynthDef(\pan, {
        arg dur = 1, panBus = 0, in = 0, out = 0;
        var pan, input;
        Line.kr(dur:dur, doneAction:2);
        pan = In.ar(panBus, 1);

        input = In.ar(in, 1);
        Out.ar(out, LinPan2.ar(input, pan));
    }),

    SynthDef(\splay, {
        arg dur = 1, in = 0, out = 0, spreadBus = 0, level = 1, centerBus = 1;
        var spread, center, input;
        Line.kr(dur:dur, doneAction:2);
        spread = In.ar(spreadBus, 1);
        center = In.ar(centerBus, 1);
        input = In.ar(in, 1);
        Out.ar(out, Splay.ar(input, spread, level, center));
    })
]