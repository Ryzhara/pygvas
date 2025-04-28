# GVAS<->JSON De/Serializer in Python

This Python library implements GVAS and JSON file format conversions.

1. Deserialization of UE4/5 GVAS binary files into Python classes.
2. Serialization of Python classed into JSON
3. Deserialization of JSON into Python classes.
4. Serialization of Python classes into binary GVAS format.
5. Matches all capabilities existing in https://github.com/localcc/gvas at the
   time of writing

> The internet says that GVAS stands for Game Variable and Attribute System.

Conversions to JSON are LOSSLESS but there is a caveat. Python only has 64-bit 
floating point values, so 32-bit values can have additional digits
when written to JSON. However, once converted back there should be no data changes.

One strategy to avoid potential ambiguity is storing 32-bit floats as
strings in JSON. I've got some commented out code for this process but I'll only
enable that if it becomes an issue because seeing something like 
["x": 2497.000000000003] is as confusing ast seeing 
["x": "2497"] in the JSON file.

## Credits

This library was inspired by two other projects I found when wanting to edit the
save file of an offline game, ***Islands of Insight***. After minor success and major
failure using a HEX editor, I went looking for tools. I found a few that could
convert GVAS to JSON but none were exactly what I wished for.

The most complete one (which this library used as a template) was based on RUST, but
the command line tools were binary executables.

I don't really like running arbitrary code on my machine, and I got tired of
using virtual environments to isolate them.

This is the elaborate and extensive RUST project that I used as a template:

* https://github.com/localcc/gvas
    * Uses an [MIT license.](https://github.com/localcc/gvas/blob/main/LICENSE)

The depth and completeness of the pygvas project is due to the depth and
completeness of the RUST gvas project.

Although I've delivered production code in a number of languages (K&R C, ANSI C, 
C++, PHP, C#, XSLT/XML/JavaScript, Unreal Engine C++), I knew nothing about RUST 
as a langauge when I started.

And I didn't really want to. 

Looking harder led me to the project titled "Python-GVAS-JSON-Converter", which
provided a great roadmap to fully understand the RUST code base. 
It implemented the necessary bones, but in Python. 

* https://github.com/afkaf/Python-GVAS-JSON-Converter
    * Uses <https://unlicense.org>

The full journey is described below, but first, a comparison.

## Key Differences from Rust Version

1. **Error Handling**
    - Uses Python's exception system instead of Rust's Result types
    - Simplified error hierarchy with custom exception classes

2. **Type System**
    - Uses Python's type hints and dataclasses
    - Replaces Rust enums with Python Enum classes
    - Uses Python's built-in types where appropriate, such as uuid

3. **Memory Management**
    - Relies on Python's garbage collection instead of Rust's ownership system
    - Simplified memory handling patterns

4. **Performance Considerations**
    - May be slower than Rust version due to Python's interpreted nature and 
      the use of Pydantic for JSON serialization
    - Uses Python's struct module for binary data handling
    - Maintains similar algorithmic complexity

5. **JSON Format**
    - The JSON format is close but not identical to the RUST output
    - A layer of wrapping is removed so the depth is shallower
    - There are no type-specific JSON property names (e.g., "ints", "bools", "
      structs" in ArrayProperty). I chose uniformity, instead.
    - Data types are indicated by a sibling "type" property rather than the name
      of the property
    - Summary: RUST JSON has slightly fewer characters

6. **Deserialization Hints Content**
    - There are cases where insufficient context exists in the GVAS binary to
      define the type of the next portion of the byte stream.
    - This implementation needs fewer of those hints for the known cases
      by defaulting missing type information to custom StructProperty.
    - Only GUID type hints are needed at this time for the example file/test library.
    - You can find example hints files (in JSON format) in the resources/test
      directory.

## Contributing

Please see the [CONTRIBUTING](CONTRIBUTING.md) document for guidelines on how
to contribute to this project.

## License

This library is distributed under the terms of the MIT license. See the
[LICENSE](LICENSE) file for details.

## The Journey

I had originally used the GVAS rust code to generate JSON that I was then able
to modify for my goals (visually mark puzzles in the game world as "completed",
forcibly complete puzzles, and give myself unlimited amounts of currency).

But before sharing that work (TBD) I didn't want to ask people to install RUST,
install the RUST tool, etc. I wanted a one-stop shop. I also wanted code that
that cybersecurity-aware people could easily inspect. Python is much more 
widely used than RUST.

Choosing Python lead me to Python-GVAS-JSON-Converter.

My first attempt was to modify Python-GVAS-JSON-Converter so its JSON output was closer
to that of the RUST project. However, there were puzzling areas in the Python
deserialization code that just needed to understand.

The next step was looking at the RUST code, and boy was I intimidated. Rather
than try to learn yet-another-language-from-scratch I installed the Cursor IDE
and asked Sonnet to translate RUST to Python.

That wasn't an abject failure, but after several days I gave that up and started
reading both the Python and RUST code side-by-side. And then refactored all the
Cursor-generated code.

I got reached sufficient capability for my Islands of Insight project, but
there was so much more in the RUST library. My desire for completeness
resulted in implementing everything in the RUST library. 

That would have been much harder without all the test/example GVAS files in
the RUST project. 

