#!/usr/bin/env node
/**
 * Build all skills from skills/ into infra/dist/
 * Each SKILL.md is packaged into a .skill bundle.
 */
const fs = require("fs");
const path = require("path");

const SKILLS_DIR = path.resolve(__dirname, "../skills");
const DIST_DIR = path.resolve(__dirname, "../infra/dist");

fs.mkdirSync(DIST_DIR, { recursive: true });

const skillDirs = fs
  .readdirSync(SKILLS_DIR, { withFileTypes: true })
  .filter((d) => d.isDirectory());

let built = 0;

for (const dir of skillDirs) {
  const skillPath = path.join(SKILLS_DIR, dir.name, "SKILL.md");
  if (!fs.existsSync(skillPath)) continue;

  const content = fs.readFileSync(skillPath, "utf-8");
  const outFile = path.join(DIST_DIR, `${dir.name}.skill`);
  fs.writeFileSync(outFile, content);
  console.log(`  ${dir.name}.skill`);
  built++;
}

console.log(`\n${built} skill(s) built -> infra/dist/`);
