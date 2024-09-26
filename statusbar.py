import time
from progress.bar import FillingSquaresBar
from progress.spinner import MoonSpinner

mylist = [1,2,3,4,5,6,7,8]

bar = FillingSquaresBar('Countdown', max = len(mylist))
# bar=MoonSpinner('as')
for item in mylist:
    bar.next()
    time.sleep(1)

bar.finish()