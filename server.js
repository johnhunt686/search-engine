const express = require("express");
const { execFile } = require("child_process");

const app = express();
const PORT = 3000;

app.get("/search", (req, res) => {
    const { q, setting1, setting2, setting3 } = req.query;

    if (!q) {
        return res.status(400).json({ error: "Missing query" });
    }

    // Build arguments in key=value format
    const args = [`query=${q}`];

    if (setting1) args.push(`setting1=${setting1}`);
    if (setting2) args.push(`setting2=${setting2}`);
    if (setting3) args.push(`setting3=${setting3}`);

    execFile("./build/SearchEngine", args, (err, stdout, stderr) => {
        if (err) {
            console.error("Execution error:", err);
            console.error("stderr:", stderr);
            return res.status(500).json({ error: "Execution failed" });
        }

        try {
            const result = JSON.parse(stdout);
            res.json(result);
        } catch (e) {
            console.error("Invalid JSON:", stdout);
            res.status(500).json({ error: "Invalid JSON from C++" });
        }
    });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});