from timetest import TimeTest
import numpy as np
import time

app = TimeTest('timetest')

@app
def foobar():
    for i in range(10):
        yield i


@app
def dotproduct():
    A = np.random.random((10000,100))
    B = np.random.random((10000,100))
    np.dot(A.T,B)

@app
def timer():
    time.sleep(2)

app.run()
