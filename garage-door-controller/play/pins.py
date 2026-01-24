import machine, time
print('Probe numeric pins:')
for n in range(40):
    try:
        p=machine.Pin(n)
        print('pin',n,'ok')
    except Exception:
        pass

print('Named pins via Pin.board:' , hasattr(machine.Pin,'board'))
if hasattr(machine.Pin,'board'):
    print([name for name in dir(machine.Pin.board) if not name.startswith('_')])
# check common named LED
try:
    print('LED pin:', machine.Pin('LED'))
except Exception as e:
    print('no LED name', e)