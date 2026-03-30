SynthDef(\monoGrainBuf, {
	arg dur = 1, soundbuf = 0, grainTriggerBus = 0, grainDurationBus = 0, grainRateBus = 0, grainPosBus = 0, out = 0;
	var grainTrigger, grainDuration, grainRate, grainPos, sig;
	Line.kr(dur:dur, doneAction:2);
	grainTrigger = In.ar(grainTriggerBus, 1);
	grainDuration = In.ar(grainDurationBus, 1);
	grainRate = In.ar(grainRateBus, 1);
	grainPos = In.ar(grainPosBus, 1);
	sig = GrainBuf.ar(
		numChannels: 1,
		trigger: grainTrigger,
		dur: grainDuration,
		sndbuf: soundbuf,
		rate: grainRate,
		pos: grainPos,
		interp: 2,
		pan: 0,
		envbufnum: -1);
	Out.ar(out, sig);
});