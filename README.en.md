# Blender UV Workflow

A Blender extension and a companion AI skill for protected, editable UV candidates, explicit constraints, diagnostics, native editing, and consumer-specific review. The interface and most workflow documentation are in Chinese.

**Version 0.8.9 source preview · GPL-3.0-or-later · Blender 5.2.1 LTS / 5.3.0.** See the [full Chinese README](README.md).

## Install

The [v0.8.8 release](https://github.com/tsist/blender-uv-workflow/releases/tag/v0.8.8) provides these published assets. Build from source to try 0.8.9.

- `uv-workflow-0.8.8.zip` installs through Extensions → Install from Disk. Open the 3D View sidebar (`N`) → UV Workflow. The add-on works independently of blenderctl.
- `blender-uv-skill-20261117.zip`: extract and copy the complete `skills/blender-uv` directory into your agent's skill directory, retaining the archive's root `LICENSE` and `NOTICE.md` in that installed directory. Back up an existing installation first. The skill is guidance, not a standalone solver.
- `SHA256SUMS.txt`: SHA-256 checksums for both archives.

Do not install GitHub's automatically generated repository source archive as a Blender extension.

## Scope

Create candidates while preserving source UV layers, use native unwrap and limited repair routes, inspect stretch/overlap/density/gaps, and review actual materials and relevant poses before adoption. A numerical pass is not an artistic or production approval.

Version 0.8.9 adds **Merge micro-islands and pack** for an unadopted 2048×2048 exclusive candidate on one static triangle mesh. Select all faces. The operation requires a candidate free of pin, seam, lock, and reuse constraints and writes the result only after the checks pass.

The add-on uses Python's standard library and Blender-provided `bpy`, `bmesh`, `mathutils`, and NumPy. Optional CLI procedures require a matching [blenderctl](https://github.com/tsist/blenderctl) entry point. The CLI uses the shared integer-texel normal transfer routine. Check the version and implementation digest with `uv describe`. See [validation and reproduction limits](docs/VALIDATION.md).

Historical `F:/Blender AI/...`, `runtime/audit/...`, and Wiki references in the skill point to local evidence that is not distributed. They are not install dependencies. Replace machine-specific example paths. No game assets, textures, private audit records, credentials, or user projects are included.

Review the micro-island result with the target material before using the candidate. Exact normal-map transfer depends on the verified UV correspondence, integer texel offsets, and base-level sampling. Validate other channels, mip levels, and target engines for your project.

## Build and license

Use `python scripts/build_release.py --output <new-directory>` to build packages for this checkout with the standard library. Verify them against the generated `SHA256SUMS.txt`. See [publishing notes](docs/PUBLISHING.md).

[GPL-3.0-or-later](LICENSE). See [NOTICE.md](NOTICE.md) for provenance and external dependencies. This license grants no rights to third-party assets.
