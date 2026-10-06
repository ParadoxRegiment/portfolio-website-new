let runtime = null;

const post = (type, text) => self.postMessage({ type, text });

self.onmessage = async ({ data }) => {
    try {
        if (data.type === "init") await init(data.config);
        else if (data.type === "run") runtime.run_command(data.line);
    } catch (error) {
        post("stderr", String(error));
    }
    post("done");
};

async function download(url, format) {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Couldn't load ${url} (HTTP ${response.status})`);
    return format === "text" ? response.text() : response.arrayBuffer();
}

async function init(config) {
    post("status", "Loading Python (first visit downloads ~10 MB)...");
    const { loadPyodide } = await import(`${config.indexUrl}pyodide.mjs`);
    const pyodide = await loadPyodide({ indexURL: config.indexUrl });

    pyodide.setStdout({ batched: (text) => post("stdout", text) });
    pyodide.setStderr({ batched: (text) => post("stderr", text) });
    pyodide.setStdin({ error: true });

    if (config.packages.length) {
        post("status", `Installing ${config.packages.join(", ")}...`);
        await pyodide.loadPackage("micropip");
        await pyodide.pyimport("micropip").install(config.packages);
    }

    post("status", "Loading project files...");
    const zip = await download(config.sourceUrl, "arrayBuffer");
    pyodide.unpackArchive(zip, "zip", { extractDir: "/home/pyodide/project"});

    const runtimeCode = await download(config.runtimeUrl, "text");
    pyodide.FS.writeFile("/home/pyodide/console_runtime.py", runtimeCode);
    runtime = pyodide.pyimport("console_runtime");
    runtime.setup(config.command, config.entryPoint, (png) =>
    self.postMessage({ type: "image", data: png }),
    );
}