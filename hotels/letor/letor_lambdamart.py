import pandas as pd
import os
import numpy as np
import random
import pyltr
from sklearn.model_selection import KFold, train_test_split
import pickle

def getheaders():
    with open('properties.txt', "r") as f:
        properties = f.read().splitlines()
    return properties

def bagging(df):   
    groups = df.groupby('srch_id')
    id_list = np.random.choice(df.srch_id.unique(), df.srch_id.unique().shape[0], replace=True)
    all_indices = []
    for group_id in id_list:
        all_indices += list(groups.get_group(group_id).index.values) 
    return df.iloc[np.array(all_indices)]

def get_target(hotel_set):
    hotel_set['score'] = 0
    hotel_set.loc[hotel_set['click_bool'] == 1, 'score'] = 1
    hotel_set.loc[hotel_set['booking_bool'] == 1, 'score'] = 5
    return hotel_set

def downsampling(train):
    # DOWNSAMPLING

    # use all clicked data
    pos_train = train[(train["click_bool"] == 1)]
    pos_ids = np.unique(list(pos_train.srch_id.values))

    # use a random sample of each search
    
    neg_train = train[(train["click_bool"] == 0) & (train["srch_id"].isin(pos_ids))]
    
    #groups = train.groupby('srch_id',group_keys = False).groups
    #neg_train = train.loc[[random.choice(groups.get(key)) for key in groups]]
    
    # combine these samples
    sel_train = pd.concat([pos_train, neg_train])
    
    return sel_train

def open_set(hotel_set_file, downsample = False, target = True, bagg = False):
    hotel_set = pd.read_csv(hotel_set_file)
    hotel_set.drop(hotel_set.select_dtypes(['object']), inplace=True, axis=1)
    
    if downsample == True:
        hotel_set = downsampling(hotel_set).sort_values('srch_id')
    
    if bagging == True:
        hotel_set = bagging(hotel_set).sort_values('srch_id')
        
    if target == True:
        hotel_set = get_target(hotel_set)
        y = hotel_set['score'].values
    else:
        y = None
        
    qid = hotel_set['srch_id'].values
    X = hotel_set[properties].values
        
    return hotel_set, qid, y, X

train = 'complete_files/hoteltest_training_set.csv'
test = 'complete_files/hoteltest_testing_set.csv'

properties = getheaders()
print('opening train file...')
train_set, Tqids, Ty, TX = open_set(train, downsample = True, bagg = True)
print('opening validation file...')
val_set, Vqids, Vy, VX = open_set(train)
print('opening test file...')
eval_set, Eqids, _, EX = open_set(test, target = False)

metric = pyltr.metrics.NDCG(k=5)
model = pyltr.models.LambdaMART(
    metric=metric,
    n_estimators=300,
    learning_rate=0.21,
    max_features='log2',
    query_subsample=0.5,
    max_leaf_nodes=10,
    min_samples_leaf=64,
    verbose=1,
)

print('fitting model...')
monitor = pyltr.models.monitors.ValidationMonitor(
            VX, Vy, Vqids, metric=metric)
model.fit(TX, Ty, Tqids, monitor=monitor)

print('predicting model...')
predict = model.predict(EX)
#print ('Random ranking:', metric.calc_mean_random(Tqids, Ty))
#print ('Our model:', metric.calc_mean(Tqids, Ty, predict))

print('creating results...')
result = pd.DataFrame({'srch_id' : Eqids,
                        'prop_id' : eval_set.prop_id,
#                        'target' : Ty,
                        'score' : predict})

print('sorting results...')
result = result.sort_values(by=['srch_id', 'score'], ascending=[True, False])

result['prop_id'] = result['prop_id'].astype(np.int64)

i = 1
file_destination = '../LambdaMart/results/'
result_file = 'results_%s.csv'
submission_file = 'submission_%s.csv'
model_file = 'model_%s.p'

while os.path.isfile(file_destination + result_file % str(i)):
    i += 1
result.to_csv(file_destination + result_file % str(i), index=False, header=True)
print('result file succesfully created.')

results = result.drop(axis=1, columns=['score'])

results.to_csv(file_destination + submission_file % str(i), index=False, header=True)
print('submission file succesfully created.')

print('saving model...')
pickle.dump(model, open(file_destination + model_file % str(i), "wb"))
