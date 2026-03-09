# CHANGELOG

This changelog only records significant changes.

## 0.4.0

### New Features

- **Index, Append, Len:** Implement for `SourceCollection` and `ObserverCollection`.
- **Pickle Support:** Allow PyMagba objects to be packed into Python dict, pickled, and reconstruct from the dict.
- **Field Functions:** Direct access to magnetic field functions, which support parallelization.
- **Stubs:** Add stubs for autocomplete and typehinting.

### Improvements

- **Improve Performance:** Reduce Python object parsing overhead.
- **Improve Documentation:** Add common sections for transformation and source methods for easy comprehension.

## 0.3.0

- Use PyO3's PyClass to bind directly to Magba structs.

## 0.1.0

- Initial release