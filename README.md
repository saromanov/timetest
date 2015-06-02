# timetest


# Usage
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
or
```python
def foobar():
    for i in range(10):
        yield i

app = TimeTest('timetest')
app.addTest('foobar', foobar)
app.run()
```

or
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

