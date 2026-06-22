// render_nrt.scd
(
var scorePath   = thisProcess.argv[0];
var outputPath  = thisProcess.argv[1];
var numChannels = thisProcess.argv[2].asInteger; // Read from Python
var options, score, duration;

postf("scorePath: %\n", scorePath);
postf("outputPath: %\n", outputPath);
postf("numChannels: %\n", numChannels);

options = ServerOptions.new
    .sampleRate_(96000)
    .numOutputBusChannels_(numChannels) // Dynamic!
    .maxNodes_(4096)
    .memSize_(2.pow(20));

score = Score.newFromFile(scorePath.standardizePath);
duration = score.endTime + 2.0;

score.recordNRT(
    outputFilePath: outputPath.standardizePath,
    headerFormat: "CAF",
    sampleFormat: "float",
    options: options,
    duration: duration,
    action: { 
        "RENDER_COMPLETE".postln;
        0.exit; 
    }
);
)