## Git workflow

- Never run `git add` or `git commit` yourself, even if a step in an approved plan says to commit. Always stop and
  let the user review and commit the changes themselves.

## Writing style

- Use American English, not British English, in code (identifiers, comments, log and exception messages), docs and
  commit messages, e.g. "color", "initialize", "behavior", "analyze", "canceled", "center", "license" (noun and verb).
- Don't use em dashes in prose (docs, comments, commit messages, etc.). Use a hyphen (-), comma, or period
  instead, or restructure the sentence.
- Nexus component names are capitalized, and italic where formatting allows (e.g. *StellaSpark Nexus*, *Expert API*).

## Python code style

- Code must run on every Python version in setup.py's classifiers (3.7 - 3.14). So no walrus operator (`:=`), no
  `match`, no positional-only parameters, and no `list[int]` or `X | None` type hints (use `typing.List`,
  `typing.Optional`, etc).
- Max line length is 120 characters (not the default 80).
- Use type hints
- Convert choices to `Enum` classes:
  - Members are lowercase.
  - Class name is CamelCase without a `Choices` suffix; an `Option` suffix is allowed.
  - Use a singular class name, not plural (e.g. `class Status(Enum)` or `class StatusOption(Enum)`, not `StatusChoices` or `Statuses`).
- Comments must start with a capital letter.
- Log messages must end with a dot.
- Raised (exception) messages must end with a dot.

## Changelog

- For every change, add an entry to `CHANGES.rst`, under the topmost (Unreleased) version.
- Write the entry in short, descriptive language that a user of the package understands: describe the effect of the change, not the implementation.
- Make it understandable for both technical customers (IT, civil engineering, water management, etc) and non-technical 
  people (policy makers, managers, etc), e.g. prefer "Speedup create_index()" over "Refactor create_index() batching".
- The changelog is public, so don't include sensitive information: no secrets or credentials, no internal URLs or hostnames, no customer names,
  and no exploitable details of security fixes (e.g. write "Fix pip-audit errors by bumping vulnerable packages", not which CVE is exploitable and how).

## Tests
- Run tests yourself to verify changes: `pytest` from the repo root for a quick check. `pytest.sh` runs the suite on
  every supported Python version via Docker.
- Prefer extending an existing test (extra assertions, or one more act/assert step on its setup) over adding a new
  one. When a new test is needed, write one test whose inputs combine several code paths, not one test per path.

Trade-off: weigh benefit against the number of added lines of testing code. More tests mean a slower test suite, more context/tokens for AI sessions, 
more brittle failures on trivial changes (e.g. reworded error messages), and more code for humans to maintain and comprehend.

- Do test:
  - Computational correctness of fundamental utilities.
- Don't test (or only very basically):
  - Exact contents of error messages (only status code/error type matters for a software contract).
  - Anything that would fail gracefully, so it would be discovered without consequences in production.
  - Functions/methods/classes that don't fulfill a critical business role.
