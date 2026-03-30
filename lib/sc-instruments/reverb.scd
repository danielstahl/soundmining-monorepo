/*
* Reverb
*/
[
    SynthDef(\stereoConvolutionReverb, {
        arg dur = 1, fftSize=2048, in = 0, out=0, ampBus = 0, irLeft, irRight, amp=1.0;
        var input, output, ampControl;

        Line.kr(dur:dur, doneAction:2);
        ampControl = In.ar(ampBus, 1);
        input = In.ar(in, 2);

        output = PartConv.ar(input, fftSize, [irLeft, irRight], amp);
        Out.ar(out, output * amp);
    }),

    SynthDef(\stereoHallReverb, {
        arg dur = 1, in = 0, out=0, ampBus = 0, rt60=1, stereo=0.5, lowFreq=200, lowRatio=0.5, hiFreq=4000, hiRatio=0.5, earlyDiffusion=0.5, lateDiffusion=0.5, modRate=0.2, modDepth=0.3;
        var input, output, amp;

        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        input = In.ar(in, 2);

        output = NHHall.ar(input, rt60, stereo, lowFreq, lowRatio, hiFreq, hiRatio, earlyDiffusion, lateDiffusion, modRate, modDepth);
        Out.ar(out, output * amp);
    }),

    SynthDef(\stereoFreeReverb, {
        arg dur = 1, in = 0, out=0, ampBus = 0, mix=0.33, room=0.5, damp=0.5;
        var input, output, amp;

        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        input = In.ar(in, 2);

        output = FreeVerb.ar(input, mix, room, damp);
        Out.ar(out, output * amp);
    }),

    SynthDef(\stereoGVerb, {
        arg dur = 1, in = 0, out=0, ampBus = 0, roomsize = 10, revtime = 3, damping = 0.5, inputbw = 0.5, spread =15, drylevel = 1, earlyreflevel = 0.7, taillevel = 0.5;
        var input, output, amp;

        Line.kr(dur:dur, doneAction:2);
        amp = In.ar(ampBus, 1);
        // GVerb takes mono as input
        input = Mix.new(In.ar(in, 2));

        output = GVerb.ar(input, roomsize:roomsize, revtime:revtime, damping:damping, inputbw:inputbw, spread:spread, drylevel:drylevel, earlyreflevel:earlyreflevel, taillevel:taillevel, maxroomsize:roomsize + 1);
        Out.ar(out, output * amp);
    })
]
