from timetest import TimeTest
import numpy as np

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

app.run()
