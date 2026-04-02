import cors from "cors";
import express from "express";
import { execFile } from "child_process";
const app = express();
const PORT = 3000;

app.use(cors());

app.get("/search", (req, res) => {
    const { q, demo, count } = req.query;

    if (!q) {
        return res.status(400).json({ error: "Missing query" });
    }

    // Build arguments in key=value format
    const args = [`query=${q}`];

    if (demo) args.push(`demo=${demo}`);
    if (count) args.push(`count=${count}`);

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
    console.log(`Server running on http://localhost:${3000}`);
});