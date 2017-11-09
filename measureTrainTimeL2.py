from multiprocessing import Pool
import os
from itertools import product
import time
from evaluate import evaluate


def run((nums, length)):
	train_start = time.time()
	os.system(
		'(time python api_dynmt.py datasets/train_{0}_{1} datasets/validate_{0}_{1} datasets/test_{0}_{1} -m models/model_L2_{0}_{1} -po -c configs/dynmtL2.config --train --cleanup) &> outputs/dynmt_train_L2_{0}_{1}.out'.format(
			nums, length))
	train_end = time.time()
	with open('outputs/dynmt_train_L2_{0}_{1}.out'.format(nums, length), 'r') as f:
		lines = f.readlines()
	epochs = int(filter(lambda x: x.startswith('last epoch is '), lines).strip()[14:])
	dev_blue_line = filter(lambda x: x.startswith('epoch: ' + str(epochs)), lines)
	dev_blue_line = dev_blue_line[dev_blue_line.index('best dev bleu ') + 14:]
	dev_bleu = float(dev_blue_line[:dev_blue_line.index(' ')])
	dev_blue_line = dev_blue_line[dev_blue_line.index('(epoch ') + 7:]
	best_epoch = int(dev_blue_line[:dev_blue_line.index(')')])
	translate_start = time.time()
	os.system(
		'(time python api_dynmt.py datasets/train_{0}_{1} datasets/validate_{0}_{1} datasets/test_{0}_{1} -m models/model_L2_{0}_{1} -po -c configs/dynmtL2.config --translate --cleanup) &> outputs/dynmt_translate_L2_{0}_{1}.out'.format(
			nums, length))
	translate_end = time.time()
	with open('outputs/dynmt_translate_L2_{0}_{1}.out'.format(nums, length), 'r') as f:
		lines = f.readlines()
	test_blue = float(filter(lambda x: x.startswith('test bleu: '), lines).strip()[11:-1])
	with open('datasets/test_{0}_{1}.corpus.c'.format(nums, length), 'r') as fc:
		with open('datasets/test_{0}_{1}.corpus.ll'.format(nums, length), 'r') as fll:
			with open('datasets/test_{0}_{1}.corpus.5.out'.format(nums, length), 'r') as fout:
				(nidentical, nsuccess, nparse, nfail, ntimeout) = evaluate(5, fc, fll, fout, True, True)
	return (nums, length, train_end - train_start, epochs, best_epoch, dev_bleu,
			translate_end - translate_start, test_blue, nidentical + nsuccess, nparse, nfail + ntimeout)


pool = Pool(processes=32)
results = pool.map(run, product(range(10000, 0, -1000), range(100, 0, -10)))
pool.close()
pool.join()
import csv
with open('resultsL2.csv', 'w') as f:
	csvf = csv.writer(f)
	csvf.writerow(['MaxNum', 'TrainDatsetSize', 'TrainTime', 'TotalEpochs', 'BestEpoch', 'BestDevBleu', 'TranslationTime', 'TestBleu', 'Successes', 'UnParsable', 'Failures'])
	for r in results:
		csvf.writerow([results[0], results[1], results[2], results[3], results[4], results[5], results[6], results[7], results[8], results[9], results[10]])