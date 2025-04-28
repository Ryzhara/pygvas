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

## License

This library is distributed under the terms of the Creative Commons CC BY-NC-SA 4.0. 
Also known as Attribution-NonCommercial-ShareAlike 4.0 International. See the
[LICENSE](LICENSE) file for details.

## Contributing

Please see the [CONTRIBUTING](CONTRIBUTING.md) document for guidelines on how
to contribute to this project.

## Credits

This library was inspired by two other projects I found when working to modify
GVAS files of an offline game, ***Islands of Insight***. After minor success and major
failure using a HEX editor, I went looking for tools. I found a few that could
convert GVAS to JSON but none were exactly what I wished for.

The most complete one (which this library followed as a template) was written in
Rust, but the command line tools were binary executables.

I don't really like running arbitrary code on my machine, and I got tired of
using virtual environments to isolate them.

The Rust project titled "gvas" (and sibling projects gvas2json and json2gvas) that 
I used as a template is here:

* https://github.com/localcc/gvas
    * Uses an [MIT license.](https://github.com/localcc/gvas/blob/main/LICENSE)

Although I've delivered production code in a number of languages (Prolog, K&R C, 
ANSI C, C++, PHP, C#, XSLT/XML/JavaScript, Unreal Engine C++), I knew very little 
about Rust syntax when I started.

Looking harder led me to the project titled "Python-GVAS-JSON-Converter", which
provided a great roadmap to understand the Rust code base. 
It implemented the necessary bones, but in Python. 

* https://github.com/afkaf/Python-GVAS-JSON-Converter
    * Uses <https://unlicense.org>

The full journey is described below, but first, a comparison summary.

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

## The Journey

I had originally used the GVAS rust code to generate JSON that I was then able
to modify for my goals (visually mark puzzles in the game world as "completed",
forcibly complete puzzles, and give myself unlimited amounts of currency).

I will share that work (TBD) but I didn't want to anyone to install Rust,
install the Rust CLI tools, etc. I wanted a one-stop shop. I also wanted code
that cybersecurity-aware people could easily inspect. Python is a natural
choice.

Choosing Python lead me to Python-GVAS-JSON-Converter.

My first attempt was to modify Python-GVAS-JSON-Converter to make the JSON output closer
to that of the Rust. However, there were puzzling areas in the Python
deserialization code that just begged to be understand.

That made the next step looking at the Rust code, and boy was I intimidated. In an 
attempt to avoid learning Rust, I installed the Cursor IDE
and asked Sonnet to translate Rust to Python.

That wasn't an abject failure, but after several days I gave that up and started
reading both the Python and Rust code side-by-side. And then refactored all the
Cursor-generated code.

I failed in my mission to not learn much about Rust syntax.

On the other hand, here is a pure Python library for working with Unreal Engine
GVAS files.

> #### Note
> This document was created in part with a generative AI prompt in the Cursor IDE. 