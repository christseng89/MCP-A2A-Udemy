import os
from pathlib import Path
from urllib.parse import unquote, urlparse

from fastmcp import Context, FastMCP

mcp = FastMCP(name="FileSearchServer")


def _is_safe_path(path: str, allowed_roots: list[str]) -> bool:
    """
    Validate that the path is within allowed root directories.
    Prevents path traversal attacks.
    """
    try:
        resolved_path = Path(path).resolve()
        return any(
            resolved_path.is_relative_to(Path(root).resolve())
            for root in allowed_roots
        )
    except (ValueError, OSError):
        return False


def _sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal.
    """
    if not filename or '..' in filename or '/' in filename or '\\' in filename:
        raise ValueError("Invalid filename: contains path traversal characters")
    return filename


@mcp.tool(
    name="find_file", 
    description="Search for a file in the provided root directories"
)
async def find_file(filename: str, ctx: Context) -> list[str]:
    """
    Recursively searches all file:// roots for 'filename' and
    returns all found absolute paths.
    
    Args:
        filename: Name of the file to search for (no path separators allowed)
        ctx: MCP context containing root directories
        
    Returns:
        List of absolute paths where the file was found
        
    Raises:
        ValueError: If filename contains invalid characters
    """
    # Sanitize filename to prevent path traversal
    sanitized_filename = _sanitize_filename(filename)
    
    roots = await ctx.list_roots()
    matches: list[str] = []
    allowed_roots: list[str] = []

    # Extract and validate root paths
    for root in roots:
        uri_str = str(root.uri)
        parsed = urlparse(uri_str)

        if parsed.scheme != "file":
            continue

        path = unquote(parsed.path)

        # Handle Windows paths
        if (
            os.name == "nt"
            and path.startswith("/")
            and len(path) > 2
            and path[2] == ":"
        ):
            path = path[1:]

        # Validate root path exists and is accessible
        if os.path.exists(path) and os.path.isdir(path):
            allowed_roots.append(path)

    # Search for file within validated roots
    for root_path in allowed_roots:
        try:
            for dirpath, _, files in os.walk(root_path):
                # Ensure we haven't traversed outside allowed roots
                if not _is_safe_path(dirpath, allowed_roots):
                    continue
                    
                if sanitized_filename in files:
                    full_path = os.path.join(dirpath, sanitized_filename)
                    # Double-check the final path is safe
                    if _is_safe_path(full_path, allowed_roots):
                        matches.append(full_path)
        except (OSError, PermissionError):
            # Skip inaccessible directories
            continue

    return matches


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
