# timetest


# Setup

```
git clone https://github.com/saromanov/timetest

```

## Usage

```python
from timetest import TimeTest
import numpy as np

app = TimeTest('timetest')

@app
def foobar():
    for i in range(10):
        p = i


@app
def dotproduct():
    A = np.random.random((10000,100))
    B = np.random.random((10000,100))
    np.dot(A.T,B)

app.run()
```

or simple
```python
def foobar():
    for i in range(10):
        yield i

app = TimeTest('timetest')
app.addTest('foobar', foobar)
app.run()
```

Also, you can limit each timetest with paremeters
```
expected
```
exprected time of running timetest
```
hardlimt
```
If time to running time test is greater than hard limit parameter, this time test will fail.

```python
from timetest import TimeTest
import time

def foobar():
    time.sleep(2000)
    for i in range(10):
        yield i

app = TimeTest('timetest')
app.addTest('foobar', foobar, expected=1)
app.run()
```

## LICENSE
MIT

