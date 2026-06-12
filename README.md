# Fileupload-bypass

Creates a wordlist of filenames for testing file-upload security. Upload forms often block code files (like `.php`) and only allow safe ones (like `.jpg`). This tool generates the common tricks for slipping a code file past that filter — combining the two extensions and inserting special characters in different spots. Just pick the backend language and it fills in the right code extensions to try.

## Install

```
git clone https://github.com/rdwsec/upload-bypass.git
cd upload-bypass
```

Requires Python 3. No external dependencies.

## Usage

PHP, default allowed extension (jpg), print to screen:

```
python uploadgen.py --lang php
```

Multiple languages and allowed extensions, written to a file:

```
python uploadgen.py --lang php,asp,jsp --allowed jpg,png -o wordlist.txt
```

Options:

- `--lang` backend language(s), comma-separated, or `all` (php, asp, jsp, perl, cf, py, node)
- `--allowed` allowed/benign extension(s), comma-separated (default `jpg`)
- `--name` base filename (default `shell`)
- `--case` also emit upper/mixed-case exec extensions (`.PHP`, `.Php`)
- `--no-baseline` skip the plain double-extension entries (char-injected only)
- `--chars` override the bypass-character set
- `--list-langs` list supported languages and their extensions
- `-o` write to a file (prints to stdout otherwise)

## Example output

```
shell.php
shell.php.jpg
shell.jpg.php
shell%20.php.jpg
shell.php%20.jpg
shell.jpg%20.php
shell.jpg.php%20
shell%00.php.jpg
...
```

Add a new language by adding one line to `EXT_MAP` in the script.

Note: web servers rarely execute uploaded `.py` or `.js` directly, so those languages are included for completeness rather than reliable code execution.

## Legal

For authorised security testing only. Use this against systems you own or have explicit written permission to test. The author accepts no responsibility for misuse.

## License

MIT
