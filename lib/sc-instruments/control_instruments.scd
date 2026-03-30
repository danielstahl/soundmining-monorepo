[
    SynthDef(\staticControl, {
        arg dur = 1, value = 1, out = 0;
        var lineEnv;
        lineEnv = Line.ar(start: value, end: value, dur: dur, doneAction:2);
        Out.ar(out, lineEnv);
    }),

    SynthDef(\lineControl, {
        arg dur = 1, startValue = 1, endValue = 1, out = 0;
        var lineEnv;
        lineEnv = Line.ar(start: startValue, end: endValue, dur: dur, doneAction:2);
        Out.ar(out, lineEnv);
    }),

    SynthDef(\xlineControl, {
        arg dur = 1, startValue = 1, endValue = 1, out = 0;
        var xlineEnv;
        xlineEnv = XLine.ar(start: startValue, end: endValue, dur: dur, doneAction:2);
        Out.ar(out, xlineEnv);
    }),

    SynthDef(\sineControl, {
        arg dur = 1, startValue = 1, peakValue = 1, out = 0;
        var sineEnv;
        sineEnv = EnvGen.ar(Env.sine(dur: dur, level: 1, dur: dur), doneAction:2).linlin(0, 1, startValue, peakValue);
        Out.ar(out, sineEnv);
    }),

    SynthDef(\percControl, {
        arg dur = 1, attackTime = 0.01, curve = -4, startValue = 1, peakValue = 1, out = 0;
        var percEnv;
        percEnv = EnvGen.ar(
            Env.perc(attackTime, dur - attackTime, 1, curve), doneAction:2).linlin(0, 1, startValue, peakValue);
        Out.ar(out, percEnv);
    }),

    SynthDef(\twoBlockControl, {
        arg dur = 1, levels = #[0, 0, 0], times = #[0, 0], curves = #[0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: curves).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\twoBlockSineControl, {
        arg dur = 1, levels = #[0, 0, 0], times = #[0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \sine).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\twoBlockExpControl, {
        arg dur = 1, levels = #[0, 0, 0], times = #[0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \exp).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\threeBlockControl, {
        arg dur = 1, levels = #[0, 0, 0, 0], times = #[0, 0, 0], curves = #[0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: curves).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\threeBlockSineControl, {
        arg dur = 1, levels = #[0, 0, 0, 0], times = #[0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \sine).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\threeBlockExpControl, {
        arg dur = 1, levels = #[0, 0, 0, 0], times = #[0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \exp).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\fourBlockControl, {
        arg dur = 1, levels = #[0, 0, 0, 0, 0], times = #[0, 0, 0, 0], curves = #[0, 0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: curves).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\fourBlockSineControl, {
        arg dur = 1, levels = #[0, 0, 0, 0, 0], times = #[0, 0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \sine).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\fourBlockExpControl, {
        arg dur = 1, levels = #[0, 0, 0, 0, 0], times = #[0, 0, 0, 0], out = 0;
        var env;
        env = EnvGen.ar(
            Env.new(
                levels: levels,
                times: times,
                curve: \exp).duration_(dur),
            doneAction:2);
        Out.ar(out, env);
    }),

    SynthDef(\soundAmplitudeControl, {
        arg dur = 1, in = 0, out = 0, attackTime = 0.01, releaseTime = 0.01;
        var sig, result;
        Line.kr(dur:dur, doneAction:2);
        sig = In.ar(in, 1);
        result = Amplitude.ar(in:sig, attackTime:attackTime, releaseTime:releaseTime);
        Out.ar(out, result);
    })
]