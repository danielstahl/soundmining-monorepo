// render_nrt.scd
(
var scorePath   = Main.arguments[0];
var outputPath  = Main.arguments[1];
var numChannels = Main.arguments[2].asInteger; // Read from Python
var options, score, duration;

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