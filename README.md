# GVAS<->JSON De/Serializer in Python

This Python library implements:

1. Deserialization of UE4/5 GVAS binary files into Python classes.
2. Serialization of Python classed into JSON
3. Deserialization of JSON into Python classes.
4. Serialization of Python classes into binary GVAS format.
5. Matches all capabilities existing in https://github.com/localcc/gvas at the
   time of writing

Conversions to JSON are LOSSLESS, with one exception. Python only has
64-bit (double) floating point values, so 32-bit floating point values can have
minor
modifications in a round-trip path from GVAS to JSON to GVAS. Their value
representation
is converted to 64-bit format, which differs in the 32-bit LSB and beyond.

One strategy to avoid this would be storing 32-bit float values as strings in
JSON.
However, but I'll go there only if it becomes an issue.

> FYI: The internet says that GVAS stands forGame Variable and Attribute System.

## Credits

This library was inspired by two other projects. I wanted to edit the save file
of an offline game built in Unreal Engine 4. After minor success and major
failure using a HEX editor, I went looking for tools. I found a few that could
convert GVAS to JSON but none were exactly what I wished for.

The most complete one (on which this library is based) was based on RUST, and
the tools were executables.

I don't really like running arbitrary code on my machine, and I got tired of
using virtual environments.

This is the elaborate and extensive RUST project that I used a template:

* https://github.com/localcc/gvas
    * Uses an MIT license (identical the text below).

The depth and completeness of this current project is due to the depth and
completeness of the RUST gvas package.

However, this project provided the roadmap for me to fully understand the RUST
code base, because it implemented the necessary bones, but in Python. It
provided a roadmap.

* https://github.com/afkaf/Python-GVAS-JSON-Converter
    * Uses <https://unlicense.org>

## Key Differences from Rust Version

1. **Error Handling**
    - Uses Python's exception system instead of Rust's Result types
    - Simplified error hierarchy with custom exception classes

2. **Type System**
    - Uses Python's type hints and dataclasses
    - Replaces Rust enums with Python Enum classes
    - Uses Python's built-in types where appropriate

3. **Memory Management**
    - Relies on Python's garbage collection instead of Rust's ownership system
    - Simplified memory handling patterns

4. **Performance Considerations**
    - May be slower than Rust version due to Python's interpreted nature
    - Uses Python's struct module for binary data handling
    - Maintains similar algorithmic complexity

5. **JSON Format**
    - The JSON format is close to but not identical to the RUST output.
    - One layer of wrapping is removed so the depth is shallower.
    - Did not implement unique JSON property names (e.g., "ints", "bools", "
      structs" in ArrayProperty). I leaned in favor of uniformity.
    - Data types are indicated by a sibling "type" property rather than the name
      of the property.
    - Summary: JSON from the RUST code is slightly smaller.

6. **Deserialization Hints Content**
    - There are cases where there is insufficient context in the GVAS binary to
      deserialize the next bytes.
    - This implementation needs fewer of those hints (purely by accident)
      because it makes the assumption that the next thing should be a custom
      StructProperty.
    - So, only GUID type hints are needed for this implementation.
    - You can find example hints files (in JSON format) in the resources/test
      directory.

## The Journey

I had originally used the GVAS rust code to generate JSON that I was then able
to modify for my goals (visually mark puzzles in the game world as "completed",
forcibly complete puzzles, and give myself unlimited amounts of currency).

But before sharing that work (TBD) I didn't want to ask people to install RUST,
install the RUST tool, etc. I wanted a one-stop shop. I also wanted code that
people could trust by looking at it, and Python is much more widely used than
RUST.

Naturally I wanted Python, which lead me to Python-GVAS-JSON-Converter.

I began by modifying Python-GVAS-JSON-Converter to make its JSON output closer
to that of the RUST project. But there were puzzling bits visible in the Python
deserialization code (arbitrary strings of bytes whose purpose I eventually
identified in the RUST code) that I just couldn't let go.

I would say that I don't like puzzles, but the game I was working to modify has
16,000 of them, so I can't say that. :)

The next step was looking at the RUST code, and boy was I intimidated. Rather
than try to learn yet-another-language-from-scratch I installed the Cursor IDE
and asked Sonnet to translate RUST to Python.

That wasn't an abject failure, but after several days I gave that up and started
reading both the Python and RUST code side-by-side. And then refactored all the
Cursor-generated code.

And I couldn't stop at the point where my game's JSON was fine. I had to
implement everything in the RUST library. Including scarfing all the binary test
files.

## Notes on Translation

This port aims to maintain the functionality of the original Rust library while
adapting to Python's idioms and best practices. Some key translation decisions:

1. Used dataclasses for structured data instead of Rust structs
2. Implemented custom exceptions instead of Result types
3. Used Python's built-in UUID handling for GUIDs
4. Maintained similar file format compatibility
5. Preserved the original binary format handling

## Contributing

Please see the [CONTRIBUTING](CONTRIBUTING.md) document for guidelines on how
to contribute to this project.

## License

This library is distributed under the terms of the MIT license. See the
[LICENSE](LICENSE) file for details.