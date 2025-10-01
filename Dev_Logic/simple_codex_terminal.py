import warnings
from Codex_Terminal import *  # noqa: F401,F403

warnings.warn(
    "simple_codex_terminal is deprecated; use Codex_Terminal instead",
    DeprecationWarning,
    stacklevel=2,
)

if __name__ == "__main__":
    main()
