from evaluateN import evaluate
from translateN import main as translate
import os
import sys
import shutil
import psutil

v = sys.argv[1]
mdir = sys.argv[2]
m = sys.argv[3]
p = int(sys.argv[4])
h = sys.argv[5]
k = int(sys.argv[6])

def cleanup():
	reserveFiles = [m+'.npz.best.npz',m+'.npz.best.npz.json']
	for f in os.listdir(mdir):
		if f.startswith(m):
			if not f in reserveFiles:
				os.remove(os.path.join(mdir,f))
	os.rename(m+'.npz.best.npz',m+'.npz')
	os.rename(m+'.npz.best.npz.json',m+'.npz.json')

translate(v, os.path.join(mdir,m+'.npz.dev.npz'),k)
with open(v+'.corpus.c','r') as fc:
	with open(v+'.corpus.ll', 'r') as fll:
		with open(v+'.corpus.out', 'r') as fout:
			(ni,ns,np,nf,nt) = evaluate(k,fc,fll,fout)
			print 'external progress: '+str((ni,ns,np,nf,nt))

vals = None
if os.path.exists(h):
	with open(h,'r') as history:
		line = history.readline().strip()
		if len(line) > 0:
			vals = map(lambda x:int(x), line.split('\t'))
if vals:
	hi = vals[0]
	hs = vals[1]
	hp = vals[2]
	hf = vals[3]
	ht = vals[4]
	count = vals[5]
	better = False
	if (ns+ni) > (hs+hi):
		better = True
	else:
		if np < hp:
			better = True
		else:
			if nt < ht:
				better = True
	if better:
		shutil.copy(os.path.join(mdir,m+'.npz.dev.npz'),os.path.join(mdir,m+'.npz.best.npz'))
		shutil.copy(os.path.join(mdir,m+'.npz.dev.npz.json'),os.path.join(mdir,m+'.npz.best.npz.json'))
		with open(h,'w') as history:
			history.write(str(ni)+'\t'+str(ns)+'\t'+str(np)+'\t'+str(nf)+'\t'+str(nt)+'\t0\n')
	else:
		count += 1
		if count > p:
			print 'No progress for last '+str(p)+' validations. Terminating!'
			for proc in psutil.process_iter():
				if proc.name() == 'python':
					if proc.pid != os.getpid():
						u = proc.uids()
						if os.getuid() in [u.real, u.effective, u.saved]:
							print '\t Kiliing process '+str(proc.pid)
							proc.kill()
							os.remove(h)
							cleanup()
							sys.exit(0)
		else:
			with open(h,'w') as history:
				history.write(str(hi)+'\t'+str(hs)+'\t'+str(hp)+'\t'+str(hf)+'\t'+str(ht)+'\t'+str(count)+'\n')
else:
	with open(h,'w') as history:
		shutil.copy(os.path.join(mdir,m+'.npz.dev.npz'),os.path.join(mdir,m+'.npz.best.npz'))
		shutil.copy(os.path.join(mdir,m+'.npz.dev.npz.json'),os.path.join(mdir,m+'.npz.best.npz.json'))
		history.write(str(ni)+'\t'+str(ns)+'\t'+str(np)+'\t'+str(nf)+'\t'+str(nt)+'\t0\n')

os.remove(v+'.corpus.out')
os.remove(v+'.alignment')
