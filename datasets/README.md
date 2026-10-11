# Evaluation Dataset

Each line in `v1.jsonl` is an independent JSON object. The dataset contains five small cases: parity, text normalization, numeric bounds, duplicate removal while preserving order, and vowel counting.

Required fields:

- `id`: a unique, stable identifier.
- `description`: behavior the tests must verify.
- `source_filename`: filename used when writing the code temporarily.
- `source_code`: Python implementation under test.
- `test_filename`: expected filename for the model-generated test.
- `tags`: categories for later result segmentation.

Cases must be small, deterministic, and synthetic. Filenames must be simple names such as `module.py`, with no directories. Do not include secrets, personal data, or corporate code.
