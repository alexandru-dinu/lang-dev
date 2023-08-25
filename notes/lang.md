# Ad-hoc language notes

## Comments

Single line:
```
# this is a comment
```

Multi-line:
```
# {
this is
a multi-line
comment
} #
```

## Types

### Primitive types
To simplify, we'll just use the following:
```
bool | char | u32 | i32 | f32
```

There is a special **no-op** value represented by `ellipsis` (like in Python): `...`, which matches any type.

There is no `null`.

### Composite types
- arrays of type `T` defined as `[T]`
- `string` is an alias to a char array, i.e. `[char]`

### Algebraic Data Types
**TODO**

## Declarations

### Variables and constants
```
const foo: i32 = 42;
var bar: f32 = 3.1415;
var xs: [char] = "hello"
```

### Functions

```
fn binary_search(x: i32, xs: [i32]) -> bool { ... }
```

Can use named args:
```
const exists: bool = binary_search(x=42, xs=[10, 42, 17]); # true
```

Closures can be defined by specifying partial args:
```
alias find42 = binary_search(x=42);`
const exists = find42(xs=[10, 42, 17]); # true
```

## Conventions

### Single memory region
To simplify the design, we just use a large memory region:
```
MEM = [...xxxx....xx....]
          ^       ^
          xs      x
```
The **allocator** finds regions of `MEM` of required size (e.g. `sizeof(type)`).

For instance, part of the declaration `const x: i32;` the allocator will find the "next" (optimal w.r.t. the allocator implementation) region of `sizeof(i32) == 4` bytes.

Similarly, for arrays, the allocator searches for `length * sizeof(type)` bytes, not necessarily contiguous.

### Distinction b/w pointers and regular values
Similar to the C-family languages, we use the `*` and `&` operators

```
var x: i32 = 42;
# {
pointer to a single i32 (4-byte memory region)
gets the address of x
} #
var p: *i32 = &x;

# dereference p
var y = *p + 10; # 52

# another pointer sizeof(*p) bytes away from p
var q: *i32 = p + 1;
```

## Errors
**TODO**
