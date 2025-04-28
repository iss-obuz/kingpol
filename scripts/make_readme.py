# %% ---------------------------------------------------------------------------------

import re
from pathlib import Path

import yaml

from kingpol.dataset.models import (
    Company,
    CompanyYearlyRecord,
    EntityRanking,
)
from kingpol.strings import normalize_docstring

root = Path(__file__).parent.parent.absolute()
dvclock_path = root / "dvc.lock"
readme_path = root / "README.md"

# %% ---------------------------------------------------------------------------------

with readme_path.open("r") as fh:
    content = fh.read().strip()

# %% ---------------------------------------------------------------------------------

sections = [
    tuple(s.strip() for s in re.split(r"\n+", section, maxsplit=1))
    for section in re.split(r"^(?=#)", content, flags=re.MULTILINE)
    if section
]

maintables_section = [
    i
    for i, (header, _) in enumerate(sections)
    if header.strip().endswith("Main tables")
][0]

md5_section = [
    i
    for i, (header, _) in enumerate(sections)
    if header.strip().endswith("MD5 checksums")
][0]

# %% Main tables info ----------------------------------------------------------------

tables = {
    "Companies (yearly)": CompanyYearlyRecord,
    "Companies": Company,
    "Ranking": EntityRanking,
}

key = maintables_section
section_content = []

for header, table in tables.items():
    desc = normalize_docstring(table.__doc__.split("\n\n", maxsplit=1)[0])
    text = f"* **{header}.** {desc}"
    section_content.append(text)

section_content = "\n\n".join(section_content)

section_header, _ = sections[key]
sections[key] = (section_header, section_content)

# %% Raw and auxiliary data md5 sums -------------------------------------------------

with dvclock_path.open() as fh:
    lock = yaml.safe_load(fh)

files = {"raw": {}, "aux": {}}
for stage in lock["stages"].values():
    for dep in stage["deps"]:
        path = Path(dep["path"])
        part1, part2, *_ = path.parts
        if part1 != "data" or part2 == "proc":
            continue
        if part2 not in ["raw", "aux"]:
            errmsg = f"Unexpected path '{path}' in dvc.lock"
            raise ValueError(errmsg)
        if path in files[part2] and files[part2][path] != dep["md5"]:
            errmsg = f"Inconsistent md5 checksums for '{path}' file"
            raise ValueError(errmsg)
        files[part2][path] = dep["md5"]

key = md5_section
section_header, _ = sections[key]
section_content = [
    "Below is the list of MD5 checksums for the raw and auxiliary data files"
    " needed for compiling the database."
    "\nThe checksums are read from the [dvc.lock](dvc.lock) file."
]

for part, deps in files.items():
    label = "Raw data files" if part == "raw" else "Auxiliary data files"
    header = f"* {label}"
    section_content.append(header)
    for path, md5 in deps.items():
        text = f"\t* `{path}`: `{md5}`"
        section_content.append(text)

sections[key] = (section_header, "\n\n".join(section_content))

# %% ---------------------------------------------------------------------------------

content = []
for header, text in sections:
    content.append(f"{header.strip()}\n\n{text.strip()}")

content = "\n\n".join(content)

# %% ---------------------------------------------------------------------------------

with readme_path.open("w") as fh:
    fh.write(content.strip())

# %% ---------------------------------------------------------------------------------
