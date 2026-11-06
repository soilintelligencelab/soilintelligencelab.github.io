# Soil Intelligence Lab website

Jekyll site for the Soil Intelligence Lab (PI: Feng Tao), Asian School of the Environment, NTU.
No theme or plugins, so GitHub Pages builds it as-is.

## Updating content

Most updates are edits to YAML files in `_data/`. You don't need to touch any HTML.

| What | File |
| --- | --- |
| Lab members, alumni | `_data/people.yml` (photos go in `assets/img/people/`) |
| Publications | `_data/publications.yml` (`selected: true` shows a paper on the home page) |
| News | `_data/news.yml` (newest first; first 4 appear on the home page) |
| Research themes | `_data/research.yml` |
| Openings / Teaching | `openings.md`, `teaching.md` |
| Interactive tools (Tools page, "Try it" links on Research) | `_data/tools.yml` |
| Lab authors bolded in citations | `lab_authors` in `_config.yml` |
| Address, email, social links, nav | `_config.yml` |
| NTU / ASE logos (header, footer) | `assets/img/logos/` — from the ASE Poster Templates 2025; ASE traced to vector, NTU wordmark vector + crest as transparent image; `-reverse`/`-white` variants for the dark footer |
| CV (People page) | not edited here: `scripts/update-cv.sh` copies `~/GitHub/CV-Latex/cv-fengtao.pdf` to `assets/pdf/` |

## COUSINE explorer

**Held back for now.** `tools_public: false` in `_config.yml` hides the explorer, the Tools page and their links, and
`tools/cousine/` is in `.gitignore`, so it exists only on this Mac and is never pushed. Once Cornell's Center for Technology
Licensing clears it, follow the comment above `tools_public`, and add "Try its scenarios in the
[COUSINE explorer](/tools/cousine/)." back to the Oct 2026 COUSINE item in `_data/news.yml`.

`tools/cousine/` is the COUSINE explorer: `index.html` is the lab page around it, and `app/` holds the static app
(`index.html`, `data.js`, `cousine_logo.png`, and `d3.min.js`, the chart library, so the page needs no outside server) built in the COUSINE_APP repository (`web/`). The app uses the lab's
colours; the lab page shows it in an iframe with `?embed`, which also drops the app's own header, and `app/` alone is
the full-screen version. It shows the scenarios of the paper only. After new simulations, rebuild it in COUSINE_APP and copy it over:

```bash
COUSINE_DATA_PATH=~/Drive/DATAHUB/cousine_output/cousine_site/ python ~/GitHub/COUSINE_APP/src_app/export_web.py
cp ~/GitHub/COUSINE_APP/web/lab/index.html ~/GitHub/COUSINE_APP/web/{data.js,cousine_logo.png,d3.min.js} tools/cousine/app/
```

The hero illustration (`assets/img/hero.svg`) is generated art: `python3 scripts/hero.py assets/img/hero.svg [seed]`
redraws it (a different seed gives a different arrangement). Swap in a field photo by changing the
`<img>` in `index.html`.

## Deploying on GitHub Pages

Run `scripts/update-cv.sh` before each push, so the site carries the latest CV from CV-Latex.

The site lives in the lab's GitHub organization, in the repository
[`soilintelligencelab/soilintelligencelab.github.io`](https://github.com/soilintelligencelab/soilintelligencelab.github.io)
(Settings → Pages → Deploy from branch → `main` / root), and is served at `https://soilintelligencelab.github.io/`.
Its own address keeps it apart from `phxtao.github.io`, Feng's personal site.

For a custom domain (e.g. `soilintelligencelab.org`), add a `CNAME` file with the domain and set `url`
to that domain in `_config.yml` (`baseurl` stays `""`).

## Previewing locally

macOS system Ruby can't run current Jekyll, so use Docker:

```bash
scripts/update-cv.sh && docker run --rm -p 4000:4000 -v "$PWD":/site -w /site ruby:3.3 bash -c "gem install --no-document jekyll:3.10.0 kramdown-parser-gfm webrick && jekyll serve --host 0.0.0.0 --force_polling"
```

Then open http://localhost:4000/.
