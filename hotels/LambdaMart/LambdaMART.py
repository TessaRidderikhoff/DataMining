import pyltr
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, train_test_split
import os

train_file = 'test_files/train.txt'
#test_file = 'complete_files/test.txt'
test_file = 'test_files/test.txt'
kfold = False

with open(train_file) as trainfile, \
        open(test_file) as evalfile:
    print('opening and reading train file...')
    X, y, qids, _ = pyltr.data.letor.read_dataset(trainfile)
    print('train file succesfully read.')
    print('opening and reading test file...')
    EX, Ey, Eqids, _ = pyltr.data.letor.read_dataset(evalfile)
    print('test file succesfully read.')

#metric = pyltr.metrics.NDCG(k=5, gain_type='identity')
metric = pyltr.metrics.NDCG(k=5)

print('creating model...')
model = pyltr.models.LambdaMART(
    metric=metric,
    n_estimators=11,
    learning_rate=0.02,
    max_features=0.5,
    query_subsample=0.5,
    max_leaf_nodes=10,
    min_samples_leaf=64,
    verbose=1,
)

if kfold == True:
    kf = KFold(n_splits = 2, shuffle = True)
    for train_index, val_index in kf.split(X):
        TX, VX = X[train_index], X[val_index]
        Ty, Vy = y[train_index], y[val_index]
        Tqids, Vqids = qids[train_index], qids[val_index]
        # Only needed if you want to perform validation (early stopping & trimming)
        monitor = pyltr.models.monitors.ValidationMonitor(
            VX, Vy, Vqids, metric=metric)
        print('fitting model...')
        model.fit(TX, Ty, Tqids, monitor=monitor)
else:
    #TX, Ty, Tqids = X, y, qids
    TX, VX, Ty, Vy, Tqids, Vqids = train_test_split(X, y, qids, test_size=0.2, shuffle=False)
    print('fitting model...')
    monitor = pyltr.models.monitors.ValidationMonitor(
            VX, Vy, Vqids, metric=metric)
    model.fit(TX, Ty, Tqids, monitor=monitor)

print('predicting model...')
Epred = model.predict(EX)
print ('Random ranking:', metric.calc_mean_random(Eqids, Ey))
print ('Our model:', metric.calc_mean(Eqids, Ey, Epred))

print('creating result file...')
result = pd.DataFrame({'srch_id' : Eqids,
                        'prop_id' : Ey,
                        'score' : Epred})

print('sorting results...')
result = result.sort_values(by=['srch_id', 'score'], ascending=[True, False])

result['prop_id'] = result['prop_id'].astype(np.int64)

i = 1
while os.path.isfile('results/results_%s.csv' % str(i)):
    i += 1
result.to_csv('results/results_%s.csv' % str(i), index=False, header=True)
print('result file succesfully created.')

results = result.drop(axis=1, columns=['score'])

results.to_csv('results/submission_%s.csv' % str(i), index=False, header=True)
print('submission file succesfully created.')
