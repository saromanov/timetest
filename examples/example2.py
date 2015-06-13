from timetest import TimeTest
from timetest import Expected
import time
import theano.tensor as T
import theano

def foobar():
    time.sleep(2)
    '''for i in range(10):
        yield i'''
def checker():
    time.sleep(1)
    return 42

def theano_fun():
    X = T.matrix('x')
    func = theano.function([X], X**2)
    print(func([[1,2,3],[4,5,6]]))

app = TimeTest('fun', backend='redis', show_past_results=5)
app.addTest('foobar', foobar, expected=Expected.HIGHEST, hardlimit=1)
app.addTest('checker2', checker)
#app.addTest('theano_fn', theano_fun)
app.run()
