/*
* Banks
*/
[
    SynthDef(\bankOfResonators, {
        arg dur = 1, in = 0, freqs = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        amps = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        ringTimes = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], out = 0;
        var input, sig;
        Line.kr(dur:dur, doneAction:2);
        input = In.ar(in, 1);
        sig = Klank.ar(`[freqs, amps, ringTimes ], input);
        Out.ar(out, sig);
    }),

    SynthDef(\bankOfOsc, {
        arg dur = 1, freqs = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        amps = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        phases = #[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], out = 0;
        var sig;
        Line.kr(dur:dur, doneAction:2);
        sig = Klang.ar(`[freqs, amps, phases ]);
        Out.ar(out, sig);
    })
]