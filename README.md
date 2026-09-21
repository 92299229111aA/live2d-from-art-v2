# live2d-from-art

## One-sentence production workflow

> Use $live2d-from-art to turn this reference into a faithful half-body Live2D avatar for VTube Studio and OBS, then complete the available visual and runtime checks.

The agent carries the workflow forward without repeated phase prompts, checks pose/framing and the target runtime early, distinguishes visible motion from parameter changes, and tracks evidence against package hashes. Actual facial tracking needs a device and a cooperating person; missing tests stay unverified.

See the [production workflow](references/production-workflow.md), [retrospective](references/retrospective.md), and [evidence contract](references/acceptance.md). Worked-example code remains experimental and character-specific. New helpers use Python's standard library. Run `python scripts/test_pipeline.py` to test packaging, stale evidence and release gates; these tests do not render or certify a new character.

An experimental Agent Skill for building interactive Live2D characters from artwork: faithful layer separation, hidden-area repair, code-authored MOC3, browser previews, audio-driven mouths, and restrained idle motion.

[中文说明](README.zh-CN.md) · [Skill workflow](SKILL.md) · [Worked example](references/worked-example.md)

This repository contains instructions and a character-specific code example. It is **not a universal one-click image-to-Live2D converter**. A coding agent must adapt masks, geometry, coordinates and parameters for each character. Loading successfully is not proof of visual quality.

## Install

```bash
npx skills add fifteen42/live2d-from-art
```

Alternatively, copy this repository into your agent's skills directory as `live2d-from-art`. Keep `SKILL.md`, `references`, `scripts` and `assets` together. For Codex, the usual personal location is `~/.codex/skills/live2d-from-art`.

Example request:

> Use $live2d-from-art to build an interactive Live2D character from my artwork. Preserve the original face, preview the real model beside the reference, and verify blinking, mouth motion and natural idle movement.

Skill installation does not install Python, render libraries or artwork. Tool and execution availability depend on the host agent.

## What is included

- `SKILL.md`: entry point and staged workflow.
- `references/`: artwork preparation, direct MOC3 authoring, animation, validation and example adaptation.
- `scripts/check_runtime.py`: dependency-free local model manifest checker (Python 3.9+).
- `assets/worked-example/character/`: the actual authoring/preview scripts from the experiment.
- `assets/worked-example/tooling/py-moc3/`: third-party MIT serializer source and its original license.

## Using the example code

1. Read [the adaptation guide](references/worked-example.md). Preserve the sibling `character/` and `tooling/` layout in a separate working directory.
2. Supply your own `Reference.png` and any required underpaint. Review and adapt all character-specific masks, coordinates and names before running extraction.
3. Install Pillow, NumPy and OpenCV in a project environment; PSD export additionally needs psd-tools. The example's private psd-tools calls require verification against your installed version.
4. Follow the documented extraction → eye/mouth preparation → hair preparation → MOC build sequence. For native validation, set `CUBISM_CORE_LIBRARY` to a compatible, legitimately obtained Cubism Core dynamic library. Web validation is an alternative.
5. Supply compatible Cubism Core, Pixi and Live2D adapter files for the `vendor/` paths referenced by the example HTML. Review their respective licenses. The previous experiment used Web Core 5.1 and native Core 5.0; this is not a claim of compatibility with every SDK version.
6. Serve your prepared character directory locally, then inspect the actual rendered model:

```bash
python3 -m http.server 18870 --bind 127.0.0.1
```

For the local manifest check:

```bash
python3 scripts/check_runtime.py /path/to/Original.model3.json
```

This checks file references, not binary validity or aesthetics. Use actual Core loading and visual inspection as separate checks. The example packager should be adapted to include only intended output files.

## Limitations

- Experimental direct MOC3 serialization, not an official Cubism exporter; no `.cmo3` editor project is generated.
- Example geometry supports shallow turns, not a fully authored side profile.
- Mouth movement follows audio amplitude, not phonemes/visemes.
- Browser validation does not certify VTube Studio compatibility.
- Character artwork, generated underpaint, audio and proprietary runtime binaries are deliberately not distributed.
- The latest calm-motion revision was checked in the original local project. This stripped code repository has been checked for syntax and manifest-checker behavior; it is not a standalone rendered demo.

The documentation is primarily Chinese; this README provides an English entry point.

## Licensing

The bundled `py-moc3` code retains its [upstream MIT license](assets/worked-example/tooling/py-moc3/LICENSE). No repository-wide license has been selected for the remaining material yet; public availability alone does not grant a general redistribution license. Live2D Core/SDK and other renderer dependencies have separate terms and are not included.
