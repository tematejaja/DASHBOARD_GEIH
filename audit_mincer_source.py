import geih
import inspect

with open('audit_mincer.txt', 'w', encoding='utf-8') as f:
    f.write(inspect.getsource(geih.EcuacionMincer.estimar))
    f.write("\n\n")
    f.write(inspect.getsource(geih.EcuacionMincer))
