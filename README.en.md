# Blender UV Workflow

A Blender extension and a companion AI skill for protected, editable UV candidates, explicit constraints, diagnostics, native editing, and consumer-specific review. The interface and most workflow documentation are in Chinese.

**Version 0.8.7 · GPL-3.0-or-later · Blender 5.2+ · Preview release.** See the [full Chinese README](README.md).

## Install

Download the assets from [v0.8.7](https://github.com/tsist/blender-uv-workflow/releases/tag/v0.8.7):

- `uv-workflow-0.8.7.zip`: use Blender's Extensions → Install from Disk, then enable UV Workflow. Open the 3D View sidebar (`N`) → UV Workflow. The add-on works without blenderctl.
- `blender-uv-skill-20261117.zip`: extract and copy the complete `skills/blender-uv` directory into your agent's skill directory, retaining the archive's root `LICENSE` and `NOTICE.md` in that installed directory. Back up an existing installation first. The skill is guidance, not a standalone solver.
- `SHA256SUMS.txt`: SHA-256 checksums for both archives.

Do not install GitHub's automatically generated repository source archive as a Blender extension.

## Scope

Create candidates while preserving source UV layers, use native unwrap and limited repair routes, inspect stretch/overlap/density/gaps, and review actual materials and relevant poses before adoption. A numerical pass is not an artistic or production approval.

The add-on uses only Python's standard library and Blender-provided `bpy`, `bmesh`, `mathutils`, and NumPy. This repository does not ship the complete blenderctl project. Optional CLI procedures in the skill require a separate, matching complete CLI; the local validation baseline was CLI 0.88.0 / UV 0.8.7. Do not assume the current public [blenderctl](https://github.com/tsist/blenderctl) branch matches that baseline.

The released production modules and skill text are unchanged from the validated local delivery. Local reports recorded 33 type cases, 7 integrity cases, 14 CLI regression tests, and visible GUI rejection/cache-reset/recovery. See [validation and reproduction limits](docs/VALIDATION.md).

Historical `F:/Blender AI/...`, `runtime/audit/...`, and Wiki references in the skill point to local evidence that is not distributed. They are not install dependencies. Replace machine-specific example paths. No game assets, textures, private audit records, credentials, or user projects are included.

One character hand-quality repair remains stopped and incomplete. The RE3 2K normal-map result is limited to the tested static case. Cross-asset generalization and engine/TBN/mip/compression/LOD/full-PBR/animation production validation remain future work.

## Build and license

Use `python scripts/build_release.py --output <new-directory>` to build packages with the standard library. Extracted contents correspond to the release archives; ZIP metadata can differ from the frozen original release assets. See [publishing notes](docs/PUBLISHING.md).

[GPL-3.0-or-later](LICENSE). See [NOTICE.md](NOTICE.md) for provenance and external dependencies. This license grants no rights to third-party assets.
