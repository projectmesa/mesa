import toml

# This file reads the pyproject.toml and prints out the
# dependencies and dev dependencies.
# It is located in tests/ folder so as not to pollute the root repo.
c = toml.load("pyproject.toml")
print("\n".join(c["project"]["dependencies"]))
print("\n".join(c["project"]["optional-dependencies"]["dev"]))
