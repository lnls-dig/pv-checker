# PV Checker

The `pv_checker.py` script is a utility for validating process variable (PV)
conditions from a `.pvchk` file.

## Usage
```
pv_checker.py <filename>
```


## `.pvchk` file format

The input file should have one condition per line in the format

```
<PV_Name> <operator> <value>
```

Brace expansion is implemented, so patterns like `PVName{01..10}` or
`PVName{One,Two}` will expand to multiple PVs.
Lines starting with `#` and empty lines are ignored.

### Supported Operators

 * `==`, `!=`, `<`, `<=`, `>`, `>=`

### Value Types

 * Numeric values (Int or Floats)
 * String (Enclosed in double `"` or single `'` quotes)

## Example input file

```
# Check if PVs are zero
PV:Temperature{01..10}-RB == 0

# Check if pressure is within range
PV:Pressure-One-RB >= 0.3

# Check string values
PV:Status-RB == "ON"

```

## Example output file


```
PV Name                                         Result     Actual               Expected
----------------------------------------------------------------------------------------------------
PV:Temperature01-RB                             Pass       0                   == 0
PV:Temperature02-RB                             Fail       1                   == 0
PV:Pressure-One-RB                              Pass       0.5                 >= 0.3
PV:Status-RB                                    Pass       'ON'                == "ON"
```
