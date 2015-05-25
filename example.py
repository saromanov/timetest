from timetest import TimeTest

app = TimeTest(backend='redis')

@app
def foobar():
    for i in range(10):
        p = i



app.addTest('foobar', foobar)
app.run()
