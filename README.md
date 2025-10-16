# Fair Billing

A Python program that processes session log files to calculate billing information.

## Usage

```bash
python3 fair_billing.py <logfile>
```

## Requirements

- Python 3.x (uses only standard library)
- Input file with format: `HH:MM:SS USERNAME Start/End`
- nose2 (for running tests)

## Algorithm

The program matches End events with the most recent available Start events for each user.
Unmatched End events assume session started at the earliest time in the file.
Unmatched Start events assume session ended at the latest time in the file.

## Testing

Install nose2:
```bash
pip install nose2
```

Run tests:
```bash
nose2
```

## Example

Run with the provided test data:
```bash
python3 fair_billing.py test_data.txt
```

Expected output:
```
ALICE99 4 240
CHARLIE 3 37
```
