from pathlib import Path
import re
import subprocess

import mca

base_path = Path(mca.__file__).parent

block_path = base_path / "blocks"
pot_path = "messages.pot"

subprocess.run(["pybabel", "extract", base_path / "framework",
                base_path / "gui", "-o", "messages.pot"])

with open(pot_path, "a") as pot_file:
    tag_set = set()
    for block in block_path.iterdir():
        # Skip pycache and init files
        if "__" in str(block):
            continue
        # Open a block file and read its content
        with open(block, mode="r") as block_file:
            content = block_file.read()

        name_matches = re.findall(r"name\s*=\s*(\"[^\"]+\")", content)
        if name_matches:
            for name in name_matches:
                pot_file.write(f"msgid {name}\n")
                pot_file.write(f"msgstr \"\"\n\n")
        # Match description strings
        description_matches = re.findall(r"(description\s*=\s*\(?)((\s*\"[^\"]+\"\s*\\?\s*)+)(\)?)", content)
        if description_matches:
            for description_match in description_matches:
                description = description_match[1]
                description = description.strip()

                # If the description is a multine string then it has to be
                # formatted differently
                if "\n" in description:
                    lines = description.split("\n")
                    lines = [line.strip("\\") for line in lines]
                    stripped_lines = [line.strip() for line in lines]
                    description = "\n".join(stripped_lines)
                    pot_file.write(f"msgid \"\"\n{description}\n")
                    pot_file.write(f"msgstr \"\"\n\"\"\n\n")
                else:
                    pot_file.write(f"msgid {description}\n")
                    pot_file.write(f"msgstr \"\"\n\n")
        # Match the choices of ChoiceParameters
        choice_matches = re.findall(
            r"(choices\s*=\s*\()((\s*\(\s*\"[^\"]+\"\s*,\s*\"[^\"]+\"\s*\),?)+)\s*\)", content)
        if choice_matches:
            for choice_match in choice_matches:
                choices = choice_match[1].split(",")
                # Only match the display string which is the second string in the
                # tuple
                for i in range(1, len(choices), 2):
                    choice = choices[i].strip()
                    # Remove closing bracket and potential other characters
                    choice = re.search(r"\"[^\"]+\"", choice).group(0)
                    pot_file.write(f"msgid {choice}\n")
                    pot_file.write(f"msgstr \"\"\n\n")
        # Match all tags of a block class
        tag_match = re.search(r"(tags\s*=\s*\()([^\)]+)(\))", content)
        # Add the tag to a set to avoid duplicate matches
        if tag_match:
            tags = tag_match.group(2).split(",")
            for tag in tags:
                if tag:
                    tag_set.add(tag)

    for tag in tag_set:
        pot_file.write(f"msgid {tag}\n")
        pot_file.write(f"msgstr \"\"\n\n")
