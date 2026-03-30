(
    var root, sourceDir, targetDir, compileFunc;

    // 1. PATH SETUP
    root = PathName(thisProcess.nowExecutingPath).pathOnly.dirname.dirname;
    sourceDir = root +/+ "lib/sc-instruments";
    targetDir = root +/+ "tools/sc/synthdefs";

    // Ensure the binary folder exists
    if(File.exists(targetDir).not) { File.mkdir(targetDir) };

    // 2. COMPILATION LOGIC
    compileFunc = { |item, fileName|
        if(item.isKindOf(SynthDef)) {
            postf("  -> Writing binary: %\n", item.name);
            item.writeDefFile(targetDir);
        } {
            postf(" Skipping item in %: Not a SynthDef (Type: %)\n", fileName, item.class);
        };
    };

    "--- 🔨 Soundmining: Global Synth Compiler ---".postln;
    postf("Source: %\nTarget: %\n\n", sourceDir, targetDir);

    // 3. ITERATE THROUGH FILES
    PathName(sourceDir).entries.do({ |file|
        if(file.extension == "scd") {
            var result;
            postf("Processing file: %\n", file.fileName);
            
            // Load the file and catch any syntax errors
            try {
                result = file.fullPath.load;
                
                case
                { result.isKindOf(SynthDef) } {
                    compileFunc.value(result, file.fileName);
                }
                { result.isKindOf(Array) } {
                    result.do({ |subItem| compileFunc.value(subItem, file.fileName) });
                }
                { result.isNil } {
                    postf(" Error: % returned nil. (Check for missing brackets or stray semicolons)\n", file.fileName);
                };
                
            } { |error|
                postf(" Compilation Error in %:\n     %\n", file.fileName, error);
            };
        };
    });

    "\nCreated SynthDefs in tools/sc/synthdefs/".postln;
    0.exit; 
)