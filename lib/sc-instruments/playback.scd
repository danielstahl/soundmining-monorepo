/*
* Playback
*/
[
    SynthDef(\stereoPlayBuffer, {
        arg bufNum, rate = 1, start = 0, end = 0, out = 0, ampBus = 0;
        var totalDur, startFrame, endFrame, amp;

        totalDur = ((end - start) / rate).abs;

        startFrame = (start / BufDur.kr(bufNum)) * BufFrames.kr(bufNum);
        endFrame = (end / BufDur.kr(bufNum)) * BufFrames.kr(bufNum);
        Line.kr(dur:totalDur, doneAction:2);
        amp = In.ar(ampBus, 1);

        Out.ar(out,
            BufRd.ar(2, bufNum,
                Line.ar(startFrame, endFrame, totalDur, doneAction:2)) * amp);
    }),

    SynthDef(\monoPlayBuffer, {
        arg bufNum, rate = 1, start = 0, end = 0, out = 0, ampBus = 0;
        var totalDur, startFrame, endFrame, amp;

        totalDur = ((end - start) / rate).abs;

        startFrame = (start / BufDur.kr(bufNum)) * BufFrames.kr(bufNum);
        endFrame = (end / BufDur.kr(bufNum)) * BufFrames.kr(bufNum);
        Line.kr(dur:totalDur, doneAction:2);
        amp = In.ar(ampBus, 1);

        Out.ar(out,
            BufRd.ar(1, bufNum,
                Line.ar(startFrame, endFrame, totalDur, doneAction:2)) * amp);
    })
]