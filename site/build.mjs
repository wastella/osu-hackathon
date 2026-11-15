// Inlines the dataset CSV into the page so it works as one self-contained file.
// Usage: node site/build.mjs data/Sleep_health_and_lifestyle_dataset.csv
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
const here = dirname(fileURLToPath(import.meta.url));
const csv = readFileSync(process.argv[2] ?? join(here, "../data/Sleep_health_and_lifestyle_dataset.csv"), "utf8").trim();
const tpl = readFileSync(join(here, "template.html"), "utf8");
writeFileSync(join(here, "index.html"), tpl.replace("__CSV__", () => csv));
console.log(`site/index.html written (${csv.split("\n").length - 1} rows)`);
