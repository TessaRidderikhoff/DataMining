import pyltr
import pandas as pd

with open('train.txt') as trainfile, \
        open('test.txt') as evalfile:
    TX, Ty, Tqids, _ = pyltr.data.letor.read_dataset(trainfile)
    EX, Ey, Eqids, _ = pyltr.data.letor.read_dataset(evalfile)

metric = pyltr.metrics.NDCG(k=5, gain_type='identity')

# Only needed if you want to perform validation (early stopping & trimming)
#monitor = pyltr.models.monitors.ValidationMonitor(
#    VX, Vy, Vqids, metric=metric, stop_after=250)

model = pyltr.models.LambdaMART(
    metric=metric,
    n_estimators=10,
    learning_rate=0.02,
    max_features=0.5,
    query_subsample=0.5,
    max_leaf_nodes=10,
    min_samples_leaf=64,
    verbose=1,
)

model.fit(TX, Ty, Tqids)
#model.fit(TX, Ty, Tqids, monitor=monitor)

Epred = model.predict(EX)
print(Epred)
print ('Random ranking:', metric.calc_mean_random(Eqids, Ey))
print ('Our model:', metric.calc_mean(Eqids, Ey, Epred))

result = pd.DataFrame({'srch_id' : Eqids,
                        'prop_id' : Ey,
                        'score' : Epred})

result = result.sort_values(by=['srch_id', 'score'], ascending=[True, False])

result.to_csv('results.csv')
