#!/usr/bin/env node
/**
 * Lint all skills — checks that each skill directory has a valid SKILL.md
 * with required YAML frontmatter fields.
 */
const fs = require("fs");
const path = require("path");

const SKILLS_DIR = path.resolve(__dirname, "../skills");
const REQUIRED_FIELDS = ["name", "description"];

const skillDirs = fs
  .readdirSync(SKILLS_DIR, { withFileTypes: true })
  .filter((d) => d.isDirectory());

let errors = 0;

for (const dir of skillDirs) {
  const skillPath = path.join(SKILLS_DIR, dir.name, "SKILL.md");

  if (!fs.existsSync(skillPath)) {
    console.error(`[WARN] ${dir.name}/ — no SKILL.md found`);
    continue;
  }

  const content = fs.readFileSync(skillPath, "utf-8");

  // Check YAML frontmatter
  if (!content.startsWith("---")) {
    console.error(`[ERROR] ${dir.name}/SKILL.md — missing YAML frontmatter`);
    errors++;
    continue;
  }

  const fmEnd = content.indexOf("---", 3);
  if (fmEnd === -1) {
    console.error(`[ERROR] ${dir.name}/SKILL.md — unclosed YAML frontmatter`);
    errors++;
    continue;
  }

  const frontmatter = content.substring(3, fmEnd);
  for (const field of REQUIRED_FIELDS) {
    if (!frontmatter.includes(`${field}:`)) {
      console.error(
        `[ERROR] ${dir.name}/SKILL.md — missing required field: ${field}`
      );
      errors++;
    }
  }

  console.log(`  [OK] ${dir.name}`);
}

if (errors > 0) {
  console.error(`\n${errors} error(s) found`);
  process.exit(1);
} else {
  console.log(`\nAll skills valid.`);
}
